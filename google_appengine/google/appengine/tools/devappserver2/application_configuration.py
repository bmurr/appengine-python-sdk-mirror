#!/usr/bin/env python
#
# Copyright 2007 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Stores application configuration taken from e.g. app.yaml, index.yaml."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import errno
import logging
import os
import random
import string
import threading

# pylint: disable=g-import-not-at-top
from google.appengine.api import appinfo
from google.appengine.api import appinfo_includes
from google.appengine.api import backendinfo
from google.appengine.api import dispatchinfo
from google.appengine._internal import six

from google.appengine.tools import queue_xml_parser
from google.appengine.tools.devappserver2 import constants
from google.appengine.tools.devappserver2 import errors

# Constants passed to functions registered with
# ModuleConfiguration.add_change_callback.
NORMALIZED_LIBRARIES_CHANGED = 1
SKIP_FILES_CHANGED = 2
HANDLERS_CHANGED = 3
INBOUND_SERVICES_CHANGED = 4
ENV_VARIABLES_CHANGED = 5
ERROR_HANDLERS_CHANGED = 6
NOBUILD_FILES_CHANGED = 7

# entrypoint changes are needed for modern runtimes(at least Python3).
# For Python3, adding/removing entrypoint can trigger re-creation of the local
# virtualenv.
ENTRYPOINT_ADDED = 8
ENTRYPOINT_CHANGED = 9  # changes from a non-empty value to non-empty value
ENTRYPOINT_REMOVED = 10

APP_ENGINE_APIS_CHANGED = 11





_HEALTH_CHECK_DEFAULTS = {
    'enable_health_check': True,
    'check_interval_sec': 5,
    'timeout_sec': 4,
    'unhealthy_threshold': 2,
    'healthy_threshold': 2,
    'restart_threshold': 60,
    'host': '127.0.0.1'
}


def java_supported():
  """True if this SDK supports running Java apps in the dev appserver."""
  return False


class ModuleConfiguration(object):
  """Stores module configuration information.

  Most configuration options are mutable and may change any time
  check_for_updates is called. Client code must be able to cope with these
  changes.

  Other properties are immutable (see _IMMUTABLE_PROPERTIES) and are guaranteed
  to be constant for the lifetime of the instance.
  """

  _IMMUTABLE_PROPERTIES = [('application', 'application'),
                           ('version', 'major_version'), ('runtime', 'runtime'),
                           ('threadsafe', 'threadsafe'),
                           ('module', 'module_name'),
                           ('basic_scaling', 'basic_scaling_config'),
                           ('manual_scaling', 'manual_scaling_config'),
                           ('automatic_scaling', 'automatic_scaling_config')]

  def __init__(self,
               config_path,
               app_id=None,
               runtime=None,
               env_variables=None):
    """Initializer for ModuleConfiguration.

    Args:
      config_path: A string containing the full path of the yaml or xml file
        containing the configuration for this module.
      app_id: A string that is the application id, or None if the application id
        from the yaml or xml file should be used.
      runtime: A string that is the runtime to use, or None if the runtime from
        the yaml or xml file should be used.
      env_variables: A dictionary that is the environment variables passed by
        flags.

    Raises:
      errors.DockerfileError: Raised if a user supplied a Dockerfile and a
        non-custom runtime.
      errors.InvalidAppConfigError: Raised if a user select python
        vanilla runtime.
    """
    self._config_path = config_path
    self._forced_app_id = app_id
    root = os.path.dirname(config_path)

    self._application_root = os.path.realpath(root)
    self._last_failure_message = None

    self._app_info_external, files_to_check = self._parse_configuration(
        self._config_path)

    # This if-statement is necessary because of following corner case
    # appinfo.EnvironmentVariables.Merge({}, None) returns None
    if env_variables:
      merged_env_variables = appinfo.EnvironmentVariables.Merge(
          self._app_info_external.env_variables, env_variables)
      self._app_info_external.env_variables = merged_env_variables

    self._mtimes = self._get_mtimes(files_to_check)
    self._application = '%s~%s' % (self.partition,
                                   self.application_external_name)
    self._api_version = self._app_info_external.api_version
    self._module_name = self._app_info_external.module
    self._main = self._app_info_external.main
    self._version = self._app_info_external.version
    self._threadsafe = self._app_info_external.threadsafe
    self._basic_scaling_config = self._app_info_external.basic_scaling
    self._manual_scaling_config = self._app_info_external.manual_scaling
    self._automatic_scaling_config = self._app_info_external.automatic_scaling
    self._runtime = runtime or self._app_info_external.runtime
    self._effective_runtime = self._app_info_external.GetEffectiveRuntime()

    dockerfile_dir = os.path.dirname(self._config_path)
    dockerfile = os.path.join(dockerfile_dir, 'Dockerfile')

    if self._effective_runtime != 'custom' and os.path.exists(dockerfile):
      raise errors.DockerfileError(
          'When there is a Dockerfile in the current directory, the only '
          'supported runtime is runtime: custom.  Please switch to runtime: '
          'custom.  The devappserver does not actually use your Dockerfile, so '
          'please use either the --runtime flag to specify the runtime you '
          'want or use the --custom_entrypoint flag to describe how to start '
          'your application.')

    if self._runtime == 'python':
      logging.warning(
          'The "python" runtime specified in "%s" is not supported - the '
          '"python27" runtime will be used instead. A description of the '
          'differences between the two can be found here:\n'
          'https://developers.google.com/appengine/docs/python/python25/diff27',
          self._config_path)
    self._minor_version_id = ''.join(
        random.choice(string.digits) for _ in range(18))

    self._forwarded_ports = {}
    if self.runtime == 'vm':
      # Avoid using python-vanilla with dev_appserver
      if 'python' == self._effective_runtime:
        raise errors.InvalidAppConfigError('Under dev_appserver, '
                                           'runtime:python is not supported '
                                           'for Flexible environment.')

      # Java uses an api_version of 1.0 where everyone else uses just 1.
      # That doesn't matter much elsewhere, but it does pain us with VMs
      # because they recognize api_version 1 not 1.0.
      # TODO: sort out this situation better, probably by changing
      # Java to use 1 like everyone else.
      if self._api_version == '1.0':
        self._api_version = '1'

    self._translate_configuration_files()

    # vm_health_check is deprecated but it still needs to be taken into account
    # if it is populated.
    if self._app_info_external.health_check is not None:
      health_check = self._app_info_external.health_check
    else:
      health_check = self._app_info_external.vm_health_check

    self._health_check = _set_health_check_defaults(health_check)

    # Configure the _is_{typeof}_scaling, _instance_class, and _memory_limit
    # attributes.
    self._is_manual_scaling = None
    self._is_basic_scaling = None
    self._is_automatic_scaling = None
    self._instance_class = self._app_info_external.instance_class
    if self._manual_scaling_config or self._runtime == 'vm':
      # TODO: Remove this 'or' when we support auto-scaled VMs.
      self._is_manual_scaling = True
      self._instance_class = (
          self._instance_class or
          constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS)
    elif self._basic_scaling_config:
      self._is_basic_scaling = True
      self._instance_class = (
          self._instance_class or
          constants.DEFAULT_BASIC_SCALING_INSTANCE_CLASS)
    else:
      self._is_automatic_scaling = True
      self._instance_class = (
          self._instance_class or constants.DEFAULT_AUTO_SCALING_INSTANCE_CLASS)
    self._memory_limit = constants.INSTANCE_CLASS_MEMORY_LIMIT.get(
        self._instance_class)

  @property
  def application_root(self):
    """The directory containing the application e.g. "/home/user/myapp"."""
    return self._application_root

  @property
  def application(self):
    return self._application

  @property
  def partition(self):
    return 'dev'

  @property
  def application_external_name(self):
    return self._app_info_external.application

  @property
  def api_version(self):
    return self._api_version

  @property
  def module_name(self):
    return self._module_name or appinfo.DEFAULT_MODULE

  @property
  def main(self):
    return self._main or ''

  @property
  def major_version(self):
    return self._version

  @property
  def minor_version(self):
    return self._minor_version_id

  @property
  def version_id(self):
    if self.module_name == appinfo.DEFAULT_MODULE:
      return '%s.%s' % (self.major_version, self._minor_version_id)
    else:
      return '%s:%s.%s' % (self.module_name, self.major_version,
                           self._minor_version_id)

  @property
  def env(self):
    return self._app_info_external.env

  @property
  def entrypoint(self):
    return self._app_info_external.entrypoint

  @property
  def runtime(self):
    return self._runtime

  @property
  def effective_runtime(self):
    return self._effective_runtime

  @effective_runtime.setter
  def effective_runtime(self, value):
    self._effective_runtime = value

  @property
  def threadsafe(self):
    return self._threadsafe

  @property
  def basic_scaling_config(self):
    return self._basic_scaling_config

  @property
  def manual_scaling_config(self):
    return self._manual_scaling_config

  @property
  def automatic_scaling_config(self):
    return self._automatic_scaling_config

  @property
  def is_basic_scaling(self):
    return self._is_basic_scaling

  @property
  def is_manual_scaling(self):
    return self._is_manual_scaling

  @property
  def is_automatic_scaling(self):
    return self._is_automatic_scaling

  @property
  def normalized_libraries(self):
    return self._app_info_external.GetNormalizedLibraries()

  @property
  def skip_files(self):
    return self._app_info_external.skip_files

  @property
  def nobuild_files(self):
    return self._app_info_external.nobuild_files

  @property
  def error_handlers(self):
    return self._app_info_external.error_handlers

  @property
  def handlers(self):
    return self._app_info_external.handlers

  @property
  def inbound_services(self):
    return self._app_info_external.inbound_services

  @property
  def instance_class(self):
    return self._instance_class

  @property
  def memory_limit(self):
    return self._memory_limit

  @property
  def env_variables(self):
    return self._app_info_external.env_variables

  @property
  def app_engine_apis(self):
    return self._app_info_external.app_engine_apis

  @property
  def is_backend(self):
    return False

  @property
  def config_path(self):
    return self._config_path

  @property
  def health_check(self):
    return self._health_check

  @property
  def default_expiration(self):
    return self._app_info_external.default_expiration

  @property
  def build_env_variables(self):
    return self._app_info_external.build_env_variables

  def check_for_updates(self):
    """Return any configuration changes since the last check_for_updates call.

    Returns:
      A set containing the changes that occurred. See the *_CHANGED module
      constants.
    """
    new_mtimes = self._get_mtimes(list(self._mtimes.keys()))
    if new_mtimes == self._mtimes:
      return set()

    try:
      app_info_external, files_to_check = self._parse_configuration(
          self._config_path)
    except Exception as e:  # pylint: disable=broad-except
      failure_message = str(e)
      if failure_message != self._last_failure_message:
        logging.error('Configuration is not valid: %s', failure_message)
      self._last_failure_message = failure_message
      return set()
    self._last_failure_message = None

    self._mtimes = self._get_mtimes(files_to_check)

    for app_info_attribute, self_attribute in self._IMMUTABLE_PROPERTIES:
      app_info_value = getattr(app_info_external, app_info_attribute)
      self_value = getattr(self, self_attribute)
      if (app_info_value == self_value or app_info_value == getattr(
          self._app_info_external, app_info_attribute)):
        # Only generate a warning if the value is both different from the
        # immutable value *and* different from the last loaded value.
        continue

      if isinstance(app_info_value, six.string_types):
        logging.warning(
            'Restart the development module to see updates to "%s" '
            '["%s" => "%s"]', app_info_attribute, self_value, app_info_value)
      else:
        logging.warning('Restart the development module to see updates to "%s"',
                        app_info_attribute)

    changes = set()
    if (app_info_external.GetNormalizedLibraries() !=
        self.normalized_libraries):
      changes.add(NORMALIZED_LIBRARIES_CHANGED)
    if app_info_external.skip_files != self.skip_files:
      changes.add(SKIP_FILES_CHANGED)
    if app_info_external.nobuild_files != self.nobuild_files:
      changes.add(NOBUILD_FILES_CHANGED)
    if app_info_external.handlers != self.handlers:
      changes.add(HANDLERS_CHANGED)
    if app_info_external.inbound_services != self.inbound_services:
      changes.add(INBOUND_SERVICES_CHANGED)
    if app_info_external.env_variables != self.env_variables:
      changes.add(ENV_VARIABLES_CHANGED)
    if app_info_external.error_handlers != self.error_handlers:
      changes.add(ERROR_HANDLERS_CHANGED)

    # identify what kind of change happened to entrypoint
    if app_info_external.entrypoint != self.entrypoint:
      if app_info_external.entrypoint and self.entrypoint:
        changes.add(ENTRYPOINT_CHANGED)
      elif app_info_external.entrypoint:
        changes.add(ENTRYPOINT_ADDED)
      else:
        changes.add(ENTRYPOINT_REMOVED)

    if app_info_external.app_engine_apis != self.app_engine_apis:
      changes.add(APP_ENGINE_APIS_CHANGED)

    self._app_info_external = app_info_external
    if changes:
      self._minor_version_id = ''.join(
          random.choice(string.digits) for _ in range(18))
    return changes

  @staticmethod
  def _get_mtimes(filenames):
    filename_to_mtime = {}
    for filename in filenames:
      try:
        filename_to_mtime[filename] = os.path.getmtime(filename)
      except OSError as e:
        # Ignore deleted includes.
        if e.errno != errno.ENOENT:
          raise
    return filename_to_mtime

  def _parse_configuration(self, configuration_path):
    """Parse a configuration file (like app.yaml or appengine-web.xml).

    Args:
      configuration_path: A string containing the full path of the yaml file
        containing the configuration for this module.

    Returns:
      A tuple where the first element is the parsed appinfo.AppInfoExternal
      object and the second element is a list of the paths of the files that
      were used to produce it, namely the input configuration_path and any
      other file that was included from that one.
    """
    with open(configuration_path) as f:
      config, files = appinfo_includes.ParseAndReturnIncludePaths(f)
    if self._forced_app_id:
      config.application = self._forced_app_id

    if config.runtime == 'vm' and not config.version:
      config.version = generate_version_id()
      logging.info('No version specified. Generated version id: %s',
                   config.version)
    return config, [configuration_path] + files

  def _translate_configuration_files(self):
    """Writes YAML equivalents of certain XML configuration files."""
    # For the most part we translate files in memory rather than writing out
    # translations. But since the task queue stub (taskqueue_stub.py)
    # reads queue.yaml directly rather than being configured with it, we need
    # to write a translation for the stub to find.
    # This means that we won't detect a change to the queue.xml, but we don't
    # currently have logic to react to changes to queue.yaml either.
    web_inf = os.path.join(self._application_root, 'WEB-INF')
    queue_xml_file = os.path.join(web_inf, 'queue.xml')
    if os.path.exists(queue_xml_file):
      appengine_generated = os.path.join(web_inf, 'appengine-generated')
      if not os.path.exists(appengine_generated):
        os.mkdir(appengine_generated)
      queue_yaml_file = os.path.join(appengine_generated, 'queue.yaml')
      with open(queue_xml_file) as f:
        queue_xml = f.read()
      queue_yaml = queue_xml_parser.GetQueueYaml(None, queue_xml)
      with open(queue_yaml_file, 'w') as f:
        f.write(queue_yaml)


def _set_health_check_defaults(health_check):
  """Sets default values for any missing attributes in HealthCheck.

  These defaults need to be kept up to date with the production values in
  health_check.cc

  Args:
    health_check: An instance of appinfo.HealthCheck or None.

  Returns:
    An instance of appinfo.HealthCheck
  """
  if not health_check:
    health_check = appinfo.HealthCheck()
  for k, v in _HEALTH_CHECK_DEFAULTS.items():
    if getattr(health_check, k) is None:
      setattr(health_check, k, v)
  return health_check


class BackendsConfiguration(object):
  """Stores configuration information for a backends.yaml file."""

  def __init__(self,
               app_config_path,
               backend_config_path,
               app_id=None,
               runtime=None,
               env_variables=None):
    """Initializer for BackendsConfiguration.

    Args:
      app_config_path: A string containing the full path of the yaml file
        containing the configuration for this module.
      backend_config_path: A string containing the full path of the
        backends.yaml file containing the configuration for backends.
      app_id: A string that is the application id, or None if the application id
        from the yaml or xml file should be used.
      runtime: A string that is the runtime to use, or None if the runtime from
        the yaml or xml file should be used.
      env_variables: A dictionary that is the environment variables passed by
        flags.
    """
    self._update_lock = threading.RLock()
    self._base_module_configuration = ModuleConfiguration(
        app_config_path, app_id, runtime, env_variables)
    backend_info_external = self._parse_configuration(backend_config_path)

    self._backends_name_to_backend_entry = {}
    for backend in backend_info_external.backends or []:
      self._backends_name_to_backend_entry[backend.name] = backend
      self._changes = dict(
          (backend_name, set())
          for backend_name in self._backends_name_to_backend_entry)

  @staticmethod
  def _parse_configuration(configuration_path):
    # TODO: It probably makes sense to catch the exception raised
    # by Parse() and re-raise it using a module-specific exception.
    with open(configuration_path) as f:
      return backendinfo.LoadBackendInfo(f)

  def get_backend_configurations(self):
    return [
        BackendConfiguration(self._base_module_configuration, self, entry)
        for entry in self._backends_name_to_backend_entry.values()
    ]

  def check_for_updates(self, backend_name):
    """Return any configuration changes since the last check_for_updates call.

    Args:
      backend_name: A str containing the name of the backend to be checked for
        updates.

    Returns:
      A set containing the changes that occurred. See the *_CHANGED module
      constants.
    """
    with self._update_lock:
      module_changes = self._base_module_configuration.check_for_updates()
      if module_changes:
        for backend_changes in self._changes.values():
          backend_changes.update(module_changes)
      changes = self._changes[backend_name]
      self._changes[backend_name] = set()
    return changes


class BackendConfiguration(object):
  """Stores backend configuration information.

  This interface is and must remain identical to ModuleConfiguration.
  """

  def __init__(self, module_configuration, backends_configuration,
               backend_entry):
    """Initializer for BackendConfiguration.

    Args:
      module_configuration: A ModuleConfiguration to use.
      backends_configuration: The BackendsConfiguration that tracks updates for
        this BackendConfiguration.
      backend_entry: A backendinfo.BackendEntry containing the backend
        configuration.
    """
    self._module_configuration = module_configuration
    self._backends_configuration = backends_configuration
    self._backend_entry = backend_entry

    if backend_entry.dynamic:
      self._basic_scaling_config = appinfo.BasicScaling(
          max_instances=backend_entry.instances or 1)
      self._manual_scaling_config = None
    else:
      self._basic_scaling_config = None
      self._manual_scaling_config = appinfo.ManualScaling(
          instances=backend_entry.instances or 1)
    self._minor_version_id = ''.join(
        random.choice(string.digits) for _ in range(18))

  @property
  def application_root(self):
    """The directory containing the application e.g. "/home/user/myapp"."""
    return self._module_configuration.application_root

  @property
  def application(self):
    return self._module_configuration.application

  @property
  def entrypoint(self):
    return self._module_configuration.entrypoint

  @property
  def partition(self):
    return self._module_configuration.partition

  @property
  def application_external_name(self):
    return self._module_configuration.application_external_name

  @property
  def api_version(self):
    return self._module_configuration.api_version

  @property
  def module_name(self):
    return self._backend_entry.name

  @property
  def main(self):
    return self._module_configuration.main

  @property
  def major_version(self):
    return self._module_configuration.major_version

  @property
  def minor_version(self):
    return self._minor_version_id

  @property
  def version_id(self):
    return '%s:%s.%s' % (self.module_name, self.major_version,
                         self._minor_version_id)

  @property
  def env(self):
    return self._module_configuration.env

  @property
  def runtime(self):
    return self._module_configuration.runtime

  @property
  def effective_runtime(self):
    return self._module_configuration.effective_runtime

  @property
  def threadsafe(self):
    return self._module_configuration.threadsafe

  @property
  def basic_scaling_config(self):
    return self._basic_scaling_config

  @property
  def manual_scaling_config(self):
    return self._manual_scaling_config

  @property
  def automatic_scaling_config(self):
    return None

  @property
  def is_basic_scaling(self):
    return bool(self._basic_scaling_config)

  @property
  def is_manual_scaling(self):
    return bool(self._manual_scaling_config)

  @property
  def is_automatic_scaling(self):
    return False

  @property
  def instance_class(self):
    return self._module_configuration.instance_class

  @property
  def memory_limit(self):
    return self._module_configuration.memory_limit

  @property
  def normalized_libraries(self):
    return self._module_configuration.normalized_libraries

  @property
  def skip_files(self):
    return self._module_configuration.skip_files

  @property
  def nobuild_files(self):
    return self._module_configuration.nobuild_files

  @property
  def error_handlers(self):
    return self._module_configuration.error_handlers

  @property
  def handlers(self):
    if self._backend_entry.start:
      return [
          appinfo.URLMap(
              url='/_ah/start', script=self._backend_entry.start, login='admin')
      ] + self._module_configuration.handlers
    return self._module_configuration.handlers

  @property
  def inbound_services(self):
    return self._module_configuration.inbound_services

  @property
  def env_variables(self):
    return self._module_configuration.env_variables

  @property
  def app_engine_apis(self):
    return self._module_configuration.app_engine_apis

  @property
  def is_backend(self):
    return True

  @property
  def config_path(self):
    return self._module_configuration.config_path

  @property
  def health_check(self):
    return self._module_configuration.health_check

  @property
  def default_expiration(self):
    return self._module_configuration.default_expiration

  @property
  def build_env_variables(self):
    return self._module_configuration.build_env_variables

  def check_for_updates(self):
    """Return any configuration changes since the last check_for_updates call.

    Returns:
      A set containing the changes that occurred. See the *_CHANGED module
      constants.
    """
    changes = self._backends_configuration.check_for_updates(
        self._backend_entry.name)
    if changes:
      self._minor_version_id = ''.join(
          random.choice(string.digits) for _ in range(18))
    return changes


class DispatchConfiguration(object):
  """Stores dispatcher configuration information."""

  def __init__(self, config_path):
    self._config_path = config_path
    self._mtime = os.path.getmtime(self._config_path)
    self._process_dispatch_entries(self._parse_configuration(self._config_path))

  @staticmethod
  def _parse_configuration(configuration_path):
    # TODO: It probably makes sense to catch the exception raised
    # by LoadSingleDispatch() and re-raise it using a module-specific exception.
    with open(configuration_path) as f:
      return dispatchinfo.LoadSingleDispatch(f)

  def check_for_updates(self):
    mtime = os.path.getmtime(self._config_path)
    if mtime > self._mtime:
      self._mtime = mtime
      try:
        dispatch_info_external = self._parse_configuration(self._config_path)
      except Exception as e:  # pylint: disable=broad-except
        failure_message = str(e)
        logging.error('Configuration is not valid: %s', failure_message)
        return
      self._process_dispatch_entries(dispatch_info_external)

  def _process_dispatch_entries(self, dispatch_info_external):  # pylint: disable=missing-docstring
    path_only_entries = []
    hostname_entries = []
    for entry in dispatch_info_external.dispatch:
      parsed_url = dispatchinfo.ParsedURL(entry.url)
      if parsed_url.host:
        hostname_entries.append(entry)
      else:
        path_only_entries.append((parsed_url, entry.module))
    if hostname_entries:
      logging.warning(
          'Hostname routing is not supported by the development server. The '
          'following dispatch entries will not match any requests:\n%s',
          '\n\t'.join(str(entry) for entry in hostname_entries))
    self._entries = path_only_entries

  @property
  def dispatch(self):
    return self._entries


class ApplicationConfiguration(object):
  """Stores application configuration information."""

  def __init__(self,
               config_paths,
               app_id=None,
               runtime=None,
               env_variables=None):
    """Initializer for ApplicationConfiguration.

    Args:
      config_paths: A list of strings containing the paths to yaml files, or to
        directories containing them.
      app_id: A string that is the application id, or None if the application id
        from the yaml or xml file should be used.
      runtime: A string that is the runtime to use, or None if the runtime from
        the yaml or xml file should be used.
      env_variables: A dictionary that is the environment variables passed by
        flags.

    Raises:
      InvalidAppConfigError: On invalid configuration.
    """
    self.modules = []
    self.dispatch = None
    # It's really easy to add a test case that passes in a string rather than
    # a list of strings, so guard against that.
    assert not isinstance(config_paths, six.string_types)
    config_paths = self._config_files_from_paths(config_paths)
    for config_path in config_paths:
      # TODO: add support for backends.xml and dispatch.xml here
      if (config_path.endswith('backends.yaml') or
          config_path.endswith('backends.yml')):
        # TODO: Reuse the ModuleConfiguration created for the app.yaml
        # instead of creating another one for the same file.
        app_yaml = config_path.replace('backends.y', 'app.y')
        backends = BackendsConfiguration(app_yaml, config_path, app_id, runtime,
                                         env_variables)
        self.modules.extend(backends.get_backend_configurations())
      elif (config_path.endswith('dispatch.yaml') or
            config_path.endswith('dispatch.yml')):
        if self.dispatch:
          raise errors.InvalidAppConfigError(
              'Multiple dispatch.yaml files specified')
        self.dispatch = DispatchConfiguration(config_path)
      else:
        module_configuration = ModuleConfiguration(config_path, app_id, runtime,
                                                   env_variables)

        self.modules.append(module_configuration)
    application_ids = set(module.application for module in self.modules)
    if len(application_ids) > 1:
      raise errors.InvalidAppConfigError(
          'More than one application ID found: %s' %
          ', '.join(sorted(application_ids)))

    self._app_id = application_ids.pop()
    module_names = set()
    for module in self.modules:
      if module.module_name in module_names:
        raise errors.InvalidAppConfigError('Duplicate module: %s' %
                                           module.module_name)
      module_names.add(module.module_name)
    if self.dispatch:
      if appinfo.DEFAULT_MODULE not in module_names:
        raise errors.InvalidAppConfigError(
            'A default module must be specified.')
      missing_modules = (
          set(module_name for _, module_name in self.dispatch.dispatch) -
          module_names)
      if missing_modules:
        raise errors.InvalidAppConfigError(
            'Modules %s specified in dispatch.yaml are not defined by a yaml '
            'file.' % sorted(missing_modules))

  def _config_files_from_paths(self, config_paths):
    """Return a list of the configuration files found in the given paths.

    For any path that is a directory, the returned list will contain the
    configuration files (app.yaml and optionally backends.yaml) found in that
    directory. If the directory is a Java app (contains a subdirectory
    WEB-INF with web.xml and application-web.xml files), then the returned
    list will contain the path to the application-web.xml file, which is treated
    as if it included web.xml. Paths that are not directories are added to the
    returned list as is.

    Args:
      config_paths: a list of strings that are file or directory paths.

    Returns:
      A list of strings that are file paths.
    """
    config_files = []
    for path in config_paths:
      config_files += (
          self._config_files_from_dir(path) if os.path.isdir(path) else [path])
    return config_files

  def _config_files_from_dir(self, dir_path):
    """Return a list of the configuration files found in the given directory.

    If the directory contains a subdirectory WEB-INF then we expect to find
    web.xml and application-web.xml in that subdirectory. The returned list
    will consist of the path to application-web.xml, which we treat as if it
    included web.xml.

    Otherwise, we expect to find an app.yaml and optionally a backends.yaml,
    and we return those in the list.

    Args:
      dir_path: a string that is the path to a directory.

    Raises:
      AppConfigNotFoundError: If the application configuration is not found.

    Returns:
      A list of strings that are file paths.
    """
    web_inf = os.path.join(dir_path, 'WEB-INF')
    if java_supported() and os.path.isdir(web_inf):
      return self._config_files_from_web_inf_dir(web_inf)
    app_yamls = self._files_in_dir_matching(dir_path, ['app.yaml', 'app.yml'])
    if not app_yamls:
      or_web_inf = ' or a WEB-INF subdirectory' if java_supported() else ''
      raise errors.AppConfigNotFoundError(
          '"%s" is a directory but does not contain app.yaml or app.yml%s' %
          (dir_path, or_web_inf))
    backend_yamls = self._files_in_dir_matching(
        dir_path, ['backends.yaml', 'backends.yml'])
    return app_yamls + backend_yamls

  def _config_files_from_web_inf_dir(self, web_inf):
    """Return a list of the configuration files found in a WEB-INF directory.

    We expect to find web.xml and application-web.xml in the directory.

    Args:
      web_inf: a string that is the path to a WEB-INF directory.

    Raises:
      AppConfigNotFoundError: If the xml files are not found.

    Returns:
      A list of strings that are file paths.
    """
    required = ['appengine-web.xml', 'web.xml']
    missing = [
        f for f in required if not os.path.exists(os.path.join(web_inf, f))
    ]
    if missing:
      raise errors.AppConfigNotFoundError(
          'The "%s" subdirectory exists but is missing %s' %
          (web_inf, ' and '.join(missing)))
    return [os.path.join(web_inf, required[0])]

  @staticmethod
  def _files_in_dir_matching(dir_path, names):
    """Return a single-element list containing an absolute path to a file.

    The method accepts a list of filenames. If multiple are found, an error is
    raised. If only one match is found, the full path to this file is returned.

    Args:
      dir_path: A string base directory for searching for filenames.
      names: A list of string relative file names to seek within dir_path.

    Raises:
      InvalidAppConfigError: If the xml files are not found.

    Returns:
      A single-element list containing a full path to a file.
    """
    abs_names = [os.path.join(dir_path, name) for name in names]
    files = [f for f in abs_names if os.path.exists(f)]
    if len(files) > 1:
      raise errors.InvalidAppConfigError('Directory "%s" contains %s' %
                                         (dir_path, ' and '.join(names)))
    return files

  @property
  def app_id(self):
    return self._app_id


def get_app_error_file(module_configuration):
  """Returns application specific file to handle errors.

  Dev AppServer only supports 'default' error code.

  Args:
    module_configuration: ModuleConfiguration.

  Returns:
      A string containing full path to error handler file or
      None if no 'default' error handler is specified.
  """
  for error_handler in module_configuration.error_handlers or []:
    if not error_handler.error_code or error_handler.error_code == 'default':
      return os.path.join(module_configuration.application_root,
                          error_handler.file)
  return None


def generate_version_id(datetime_getter=datetime.datetime.now):
  """Generates a version id based off the current time.

  Args:
    datetime_getter: A function that returns a datetime.datetime instance.

  Returns:
    A version string based.
  """
  return datetime_getter().isoformat().lower().replace(':',
                                                       '').replace('-', '')[:15]
