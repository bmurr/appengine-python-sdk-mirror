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
"""Serves content for "script" handlers using the PHP runtime."""

import os
import os.path
import re
import subprocess
import sys

import google
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
if six.PY3:
  from google.appengine.api import appinfo
else:
  from google.appengine.api import appinfo

from google.appengine.tools.devappserver2 import http_runtime
from google.appengine.tools.devappserver2 import instance

from google.appengine.tools.devappserver2 import safe_subprocess

_RUNTIME_PATH = six.ensure_str(os.path.abspath(




os.path.join(os.path.dirname(sys.argv[0]), '_php_runtime.py')
))
_CHECK_ENVIRONMENT_SCRIPT_PATH = six.ensure_str(os.path.join(
    os.path.dirname(__file__), 'check_environment.php'))
_RUNTIME_ARGS = [
    # sys.executable is None in tests
    None if sys.executable is  None else six.ensure_str(sys.executable),
    _RUNTIME_PATH]

GAE_EXTENSION_NAME = 'GAE Runtime Module'

# OS-specific file naming for bundled PHP binaries. Assume empty string
# if no corresponding OS is found.
_EXECUTABLE_EXT = {'win32': '.exe'}
_EXTENSION_PREFIX = {'win32': 'php_'}
_DYNAMIC_LIB_EXT = {'win32': '.dll', 'darwin': '.so'}

_COMPOSER_FILE = 'composer.json'
_COMPOSER_LOCK_FILE = 'composer.lock'


def _get_php_executable_path(runtime):
  filename = 'php-cgi%s' % _EXECUTABLE_EXT.get(sys.platform, '')
  return _get_php_binary_path(filename, runtime)


def _get_php_extension_path(extension_stem, runtime):
  filename = '%s%s%s' % (_EXTENSION_PREFIX.get(
      sys.platform, ''), extension_stem, _DYNAMIC_LIB_EXT.get(sys.platform, ''))
  return _get_php_binary_path(filename, runtime)


def _get_php_binary_path(filename, runtime):
  """Returns the path to the siloed php-cgi binary or None if not present."""
  php_binary_dir = None
  if sys.platform == 'win32':
    if runtime == 'php55':
      php_binary_dir = 'php/php-5.5-Win32-VC11-x86'
  elif sys.platform == 'darwin':
    if runtime == 'php55':
      php_binary_dir = '../php55'

  if php_binary_dir:
    # The Cloud SDK uses symlinks in its packaging of the Mac Launcher.  First
    # try to find PHP relative to the absolute path of this executable.  If that
    # doesn't work, try using the path without dereferencing all symlinks.
    base_paths = [os.path.realpath(sys.argv[0]), sys.argv[0]]
    for base_path in base_paths:
      root = os.path.dirname(base_path)
      abs_path = os.path.abspath(os.path.join(root, php_binary_dir, filename))
      if os.path.exists(abs_path):
        return abs_path

  return None


class _PHPBinaryError(Exception):
  pass


class _PHPEnvironmentError(Exception):
  pass


class _ComposerBinaryError(Exception):
  pass


class PHPRuntimeInstanceFactory(instance.InstanceFactory,
                                instance.ModernInstanceFactoryMixin):
  """A factory that creates new PHP runtime Instances."""

  # TODO: Use real script values.
  START_URL_MAP = appinfo.URLMap(
      url='/_ah/start', script='$PHP_LIB/default_start_handler', login='admin')
  WARMUP_URL_MAP = appinfo.URLMap(
      url='/_ah/warmup',
      script='$PHP_LIB/default_warmup_handler',
      login='admin')
  SUPPORTS_INTERACTIVE_REQUESTS = True
  FILE_CHANGE_INSTANCE_RESTART_POLICY = instance.AFTER_FIRST_REQUEST

  def __init__(self, request_data, runtime_config_getter, module_configuration):
    """Initializer for PHPRuntimeInstanceFactory.

    Args:
      request_data: A wsgi_request_info.WSGIRequestInfo that will be provided
        with request information for use by API stubs.
      runtime_config_getter: A function that can be called without arguments and
        returns the runtime_config_pb2.Config containing the configuration for
        the runtime.
      module_configuration: An application_configuration.ModuleConfiguration
        instance respresenting the configuration of the module that owns the
        runtime.
    """
    super(PHPRuntimeInstanceFactory,
          self).__init__(request_data,
                         8 if runtime_config_getter().threadsafe else 1)
    self._runtime_config_getter = runtime_config_getter
    self._module_configuration = module_configuration

    if self._is_modern():
      self._run_composer()

  @classmethod
  def _check_php_version(cls, php_executable_path, env):
    """Check if php-cgi has the correct version."""
    version_process = safe_subprocess.start_process([php_executable_path, '-v'],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    env=env)
    version_stdout, version_stderr = version_process.communicate()
    if version_process.returncode:
      raise _PHPEnvironmentError(
          '"%s -v" returned an error [%d]\n%s%s' %
          (php_executable_path, version_process.returncode, version_stderr,
           version_stdout))

    version_match = re.search(r'PHP (\d+).(\d+)',
                              six.ensure_text(version_stdout))
    if version_match is None:
      raise _PHPEnvironmentError(
          '"%s -v" returned an unexpected version string:\n%s%s' %
          (php_executable_path, version_stderr, version_stdout))

    version = tuple(int(v) for v in version_match.groups())
    if version < (5, 5):
      raise _PHPEnvironmentError(
          'The PHP interpreter must be version >= 5.5, %d.%d found' % version)

  @classmethod
  def _check_gae_extension(cls, php_executable_path, gae_extension_path, env):
    """Check if GAE extension can be loaded."""
    if not os.path.exists(gae_extension_path):
      raise _PHPBinaryError('The path specified with the '
                            '--php_gae_extension_path flag (%s) does not '
                            'exist.' % gae_extension_path)

    # The GAE extension requires APPLICATION_ROOT to be set.
    env['APPLICATION_ROOT'] = os.getcwd()

    args = [
        php_executable_path, '-m', '-d',
        'extension="%s"' % os.path.basename(gae_extension_path), '-d',
        'extension_dir="%s"' % os.path.dirname(gae_extension_path)
    ]

    ext_process = safe_subprocess.start_process(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    ext_stdout, ext_stderr = ext_process.communicate()
    if ext_process.returncode:
      raise _PHPEnvironmentError(
          '"%s -m" returned an error [%d]\n%s%s' %
          (php_executable_path, ext_process.returncode, ext_stderr, ext_stdout))

    if GAE_EXTENSION_NAME not in six.ensure_text(ext_stdout):
      raise _PHPEnvironmentError('Unable to load GAE runtime module at %s' %
                                 gae_extension_path)

  @classmethod
  def _check_environment(cls, php_executable_path, env):
    # Clear auto_prepend_file & auto_append_file ini directives as they can
    # trigger error and cause non-zero return.
    args = [
        php_executable_path, '-f', _CHECK_ENVIRONMENT_SCRIPT_PATH, '-d',
        'auto_prepend_file=NULL', '-d', 'auto_append_file=NULL'
    ]
    check_process = safe_subprocess.start_process(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    check_process_stdout, _ = check_process.communicate()
    if check_process.returncode:
      raise _PHPEnvironmentError(check_process_stdout)

  @classmethod
  def _check_php_executable_path(cls, php_executable_path):
    """Perform sanity check on php-cgi & gae extension."""
    if not php_executable_path:
      raise _PHPBinaryError('The development server must be started with the '
                            '--php_executable_path flag set to the path of the '
                            'php-cgi binary.')

    if not os.path.exists(php_executable_path):
      raise _PHPBinaryError('The path specified with the --php_executable_path '
                            'flag (%s) does not exist.' % php_executable_path)

    if not os.access(php_executable_path, os.X_OK):
      raise _PHPBinaryError('The path specified with the --php_executable_path '
                            'flag (%s) is not executable' % php_executable_path)

  @classmethod
  def _check_binaries(cls, php_executable_path, php_library_path,
                      gae_extension_path):
    """Perform sanity check on php-cgi & gae extension."""
    cls._check_php_executable_path(php_executable_path)
    env = {}
    # On Windows, in order to run a side-by-side assembly the specified env
    # must include a valid SystemRoot.
    if 'SYSTEMROOT' in os.environ:
      env['SYSTEMROOT'] = os.environ['SYSTEMROOT']

    ld_library_path = []
    if php_library_path:
      ld_library_path.append(php_library_path)
    if 'LD_LIBRARY_PATH' in os.environ:
      ld_library_path.append(os.environ['LD_LIBRARY_PATH'])
    if ld_library_path:
      env['LD_LIBRARY_PATH'] = ':'.join(ld_library_path)

    cls._check_php_version(php_executable_path, env)
    cls._check_environment(php_executable_path, env)
    if gae_extension_path:
      cls._check_gae_extension(php_executable_path, gae_extension_path, env)

  def _GenerateConfigForRuntime(self):
    """Return a copy of runtime config for starting a PHP runtime instance.

    The returned config uses the bundled PHP binaries if none is specified
    already through the command line arguments.

    Returns:
      The created runtime_config_pb2.Config protobuf object.
    """

    def setattr_if_empty(obj, field, value):
      if not getattr(obj, field) and value:
        setattr(obj, field, value)

    runtime = self._module_configuration.runtime
    runtime_config = self._runtime_config_getter()

    setattr_if_empty(runtime_config.php_config, 'php_executable_path',
                     _get_php_executable_path(runtime))

    setattr_if_empty(runtime_config.php_config, 'php_library_path', '')

    setattr_if_empty(runtime_config.php_config, 'gae_extension_path',
                     _get_php_extension_path('gae_runtime_module', runtime))

    setattr_if_empty(runtime_config.php_config, 'xdebug_extension_path',
                     _get_php_extension_path('xdebug', runtime))

    return runtime_config

  def new_instance(self, instance_id, expect_ready_request=False):
    """Create and return a new Instance.

    Args:
      instance_id: A string or integer representing the unique (per module) id
        of the instance.
      expect_ready_request: If True then the instance will be sent a special
        request (i.e. /_ah/warmup or /_ah/start) before it can handle external
        requests.

    Returns:
      The newly created instance.Instance.
    """

    def instance_config_getter():
      runtime_config = self._GenerateConfigForRuntime()
      runtime_config.instance_id = str(instance_id)
      return runtime_config

    php_config = self._GenerateConfigForRuntime().php_config
    php_executable_path = php_config.php_executable_path
    if self._is_modern():
      self._check_php_executable_path(php_executable_path)
      if self._module_configuration.entrypoint:
        runtime_args = six.ensure_str(
            self._module_configuration.entrypoint.split())
      else:
        runtime_args = (
            six.ensure_str(php_executable_path), '-S', 'localhost:${PORT}',
            'index.php')

      start_process_flavor = http_runtime.START_PROCESS_WITH_ENTRYPOINT

      my_runtime_config = self._runtime_config_getter()
      env = self.get_modern_env_vars(instance_id)
      env['API_HOST'] = six.ensure_str(my_runtime_config.api_host)
      env['API_PORT'] = str(my_runtime_config.api_port)
      env['GAE_APPLICATION'] = six.ensure_str(my_runtime_config.app_id)
      for kv in my_runtime_config.environ:
        env[kv.key] = kv.value
    else:
      php_library_path = php_config.php_library_path
      gae_extension_path = six.ensure_text(php_config.gae_extension_path)

      self._check_binaries(php_executable_path, php_library_path,
                           gae_extension_path)

      runtime_args = _RUNTIME_ARGS
      start_process_flavor = http_runtime.START_PROCESS
      env = None

    proxy = http_runtime.HttpRuntimeProxy(
        runtime_args,
        instance_config_getter,
        self._module_configuration,
        env=env,
        start_process_flavor=start_process_flavor)

    return instance.Instance(self.request_data, instance_id, proxy,
                             self.max_concurrent_requests,
                             self.max_background_threads, expect_ready_request)

  def dependency_libraries_changed(self, file_changes):
    """Decide whether dependency libraries in composer.json changed.

    If these libraries changed, rerun composer. This should only be called for
    PHP7+ runtime.

    Args:
      file_changes: A set of strings, representing paths to file changes.

    Returns:
      True if dependency libraries changed.
    """
    if any(f == self._composer_file_path for f in file_changes):
      self._run_composer()
      return True
    return False

  # TODO: Find a way to avoid listing modern modules.
  def _is_modern(self):
    runtime = self._module_configuration.runtime
    return runtime.startswith('php7') or runtime.startswith('php8')

  def _run_composer(self):
    composer_file_path = self._composer_file_path
    if composer_file_path:
      php_config = self._GenerateConfigForRuntime().php_config
      php_composer_path = php_config.php_composer_path
      if not php_composer_path:
        raise _ComposerBinaryError(
            ('file {} was present but Composer binary was not found. Please ' +
             'provide --php_composer_path flag.').format(_COMPOSER_FILE))
      composer_file_dir = os.path.dirname(composer_file_path)
      if self._composer_lock_path:
        args = (php_composer_path, 'update')
      else:
        args = (php_composer_path, 'install')
      if subprocess.call(args, cwd=composer_file_dir):
        raise IOError('Unable to run composer install')

  @property
  def _composer_file_path(self):
    """Get the path of the composer file or None if the file doesn't exist."""
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(self._module_configuration.config_path),
            _COMPOSER_FILE))
    return path if os.path.exists(path) else None

  @property
  def _composer_lock_path(self):
    """Get the path of the composer file or None if the file doesn't exist."""
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(self._module_configuration.config_path),
            _COMPOSER_LOCK_FILE))
    return path if os.path.exists(path) else None
