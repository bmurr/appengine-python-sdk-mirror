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
"""Tests for google.apphosting.tools.devappserver2.application_configuration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function



import collections
from contextlib import contextmanager
import datetime
import io
import os.path
import shutil
import tempfile
import unittest
from unittest import mock

import google
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
if six.PY2:
  from google.appengine.api import appinfo
  from google.appengine.api import appinfo_includes
  from google.appengine.api import backendinfo
  from google.appengine.api import dispatchinfo
else:
  from google.appengine.api import appinfo
  from google.appengine.api import appinfo_includes
  from google.appengine.api import backendinfo
  from google.appengine.api import dispatchinfo

from google.appengine.tools.devappserver2 import application_configuration
from google.appengine.tools.devappserver2 import constants
from google.appengine.tools.devappserver2 import errors


@contextmanager
def _java_temporarily_supported():
  """Make the java_supported() function return True temporarily.

   Use as:
     with _java_temporarily_supported():
       ...test that relies on Java being supported...
  """
  old_java_supported = application_configuration.java_supported
  application_configuration.java_supported = lambda: True
  yield
  application_configuration.java_supported = old_java_supported


_DEFAULT_HEALTH_CHECK = appinfo.HealthCheck(
    enable_health_check=True,
    check_interval_sec=5,
    timeout_sec=4,
    unhealthy_threshold=2,
    healthy_threshold=2,
    restart_threshold=60,
    host='127.0.0.1')


class TestModuleConfiguration(unittest.TestCase):
  """Tests for application_configuration.ModuleConfiguration."""

  def setUp(self):
    application_configuration.open = self._fake_open

  def tearDown(self):
    del application_configuration.open

  @staticmethod
  def _fake_open(unused_filename):
    return io.BytesIO()

  def test_good_app_yaml_configuration(self):
    automatic_scaling = appinfo.AutomaticScaling(
        min_pending_latency='1.0s',
        max_pending_latency='2.0s',
        min_idle_instances=1,
        max_idle_instances=2)
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap()]
    env_variables = appinfo.EnvironmentVariables()
    info = appinfo.AppInfoExternal(
        application='app',
        entrypoint='gunicorn main:app',
        module='module1',
        version='1',
        runtime='python27',
        threadsafe=False,
        automatic_scaling=automatic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=env_variables,
    )
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')
    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual(os.path.realpath('/appdir/app.yaml'), config.config_path)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('exec gunicorn main:app', config.entrypoint)
    self.assertEqual('dev', config.partition)
    self.assertEqual('module1', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'module1:1\.\d+')
    self.assertEqual('python27', config.runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(automatic_scaling, config.automatic_scaling_config)
    self.assertTrue(config.is_automatic_scaling)
    self.assertFalse(config.is_basic_scaling)
    self.assertFalse(config.is_manual_scaling)
    self.assertEqual(config.instance_class,
                     constants.DEFAULT_AUTO_SCALING_INSTANCE_CLASS)
    self.assertEqual(
        config.memory_limit,
        constants.INSTANCE_CLASS_MEMORY_LIMIT.get(
            constants.DEFAULT_AUTO_SCALING_INSTANCE_CLASS))
    self.assertEqual(info.GetNormalizedLibraries(), config.normalized_libraries)
    self.assertEqual(r'\*.gif', config.skip_files)
    self.assertEqual(error_handlers, config.error_handlers)
    self.assertEqual(handlers, config.handlers)
    self.assertEqual(['warmup'], config.inbound_services)
    self.assertEqual(env_variables, config.env_variables)
    self.assertEqual({'/appdir/app.yaml': 10}, config._mtimes)
    self.assertEqual(_DEFAULT_HEALTH_CHECK, config.health_check)

  def test_good_app_yaml_configuration_basic_scaling(self):
    basic_scaling = appinfo.BasicScaling()
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap()]
    env_variables = appinfo.EnvironmentVariables()
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='python27',
        threadsafe=False,
        basic_scaling=basic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=env_variables,
    )
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')

    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual(os.path.realpath('/appdir/app.yaml'), config.config_path)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('dev', config.partition)
    self.assertEqual('module1', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'module1:1\.\d+')
    self.assertEqual('python27', config.runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(basic_scaling, config.basic_scaling_config)
    self.assertFalse(config.is_automatic_scaling)
    self.assertTrue(config.is_basic_scaling)
    self.assertFalse(config.is_manual_scaling)
    self.assertEqual(config.instance_class,
                     constants.DEFAULT_BASIC_SCALING_INSTANCE_CLASS)
    self.assertEqual(
        config.memory_limit, constants.INSTANCE_CLASS_MEMORY_LIMIT[
            constants.DEFAULT_BASIC_SCALING_INSTANCE_CLASS])
    self.assertEqual(info.GetNormalizedLibraries(), config.normalized_libraries)
    self.assertEqual(r'\*.gif', config.skip_files)
    self.assertEqual(error_handlers, config.error_handlers)
    self.assertEqual(handlers, config.handlers)
    self.assertEqual(['warmup'], config.inbound_services)
    self.assertEqual(env_variables, config.env_variables)
    self.assertEqual({'/appdir/app.yaml': 10}, config._mtimes)
    self.assertEqual(_DEFAULT_HEALTH_CHECK, config.health_check)

  def test_memory_limit_configuration_auto_scaling_nondefault(self):
    automatic_scaling = appinfo.AutomaticScaling()
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap()]
    env_variables = appinfo.EnvironmentVariables()
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='python27',
        threadsafe=False,
        automatic_scaling=automatic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=env_variables,
        instance_class='F4_1G',
    )
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')

    self.assertEqual(config.instance_class, 'F4_1G')
    self.assertEqual(config.memory_limit,
                     constants.INSTANCE_CLASS_MEMORY_LIMIT['F4_1G'])

  def test_memory_limit_configuration_basic_scaling_nondefault(self):
    basic_scaling = appinfo.BasicScaling()
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap()]
    env_variables = appinfo.EnvironmentVariables()
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='python27',
        threadsafe=False,
        basic_scaling=basic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=env_variables,
        instance_class='B4_1G',
    )
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')

    self.assertEqual(config.instance_class, 'B4_1G')
    self.assertEqual(config.memory_limit,
                     constants.INSTANCE_CLASS_MEMORY_LIMIT['B4_1G'])

  def test_app_yaml_with_service(self):
    handlers = [appinfo.URLMap()]
    info = appinfo.AppInfoExternal(
        application='app',
        service='module1',
        version='1',
        runtime='python27',
        threadsafe=False,
        handlers=handlers,
    )
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')

    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('module1', config.module_name)
    self.assertEqual('1', config.major_version)

  def _test_vm_app_yaml_configuration_with_env(self, env):
    manual_scaling = appinfo.ManualScaling()
    vm_settings = appinfo.VmSettings()
    vm_settings['vm_runtime'] = 'myawesomeruntime'
    vm_settings['forwarded_ports'] = '49111:49111,5002:49112,8000'
    health_check = appinfo.HealthCheck()
    health_check.enable_health_check = False
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='vm',
        env=env,
        vm_settings=vm_settings,
        threadsafe=False,
        manual_scaling=manual_scaling,
        health_check=health_check)

    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')
    self.assertEqual(env, config.env)

  def test_vm_app_yaml_configuration_with_env_2(self):
    self._test_vm_app_yaml_configuration_with_env('2')

  def test_vm_app_yaml_configuration_with_env_flex(self):
    self._test_vm_app_yaml_configuration_with_env('flex')

  def test_vm_app_yaml_configuration_with_env_flexible(self):
    self._test_vm_app_yaml_configuration_with_env('flexible')

  def test_vm_app_yaml_configuration(self):
    manual_scaling = appinfo.ManualScaling()
    vm_settings = appinfo.VmSettings()
    vm_settings['vm_runtime'] = 'myawesomeruntime'
    vm_settings['forwarded_ports'] = '49111:49111,5002:49112,8000'
    health_check = appinfo.HealthCheck()
    health_check.enable_health_check = False
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='vm',
        vm_settings=vm_settings,
        threadsafe=False,
        manual_scaling=manual_scaling,
        health_check=health_check)

    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')
    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual(os.path.realpath('/appdir/app.yaml'), config.config_path)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('dev', config.partition)
    self.assertEqual('module1', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'module1:1\.\d+')
    self.assertEqual('vm', config.runtime)
    self.assertEqual(vm_settings['vm_runtime'], config.effective_runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(manual_scaling, config.manual_scaling_config)
    self.assertFalse(config.is_automatic_scaling)
    self.assertFalse(config.is_basic_scaling)
    self.assertTrue(config.is_manual_scaling)
    self.assertEqual(config.instance_class,
                     constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS)
    self.assertEqual(
        config.memory_limit,
        constants.INSTANCE_CLASS_MEMORY_LIMIT.get(
            constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS))
    self.assertEqual({'/appdir/app.yaml': 10}, config._mtimes)
    self.assertEqual(info.health_check, config.health_check)

  def test_vm_app_yaml_configuration_network(self):
    manual_scaling = appinfo.ManualScaling()
    vm_settings = appinfo.VmSettings()
    vm_settings['vm_runtime'] = 'myawesomeruntime'
    network = appinfo.Network()
    network.forwarded_ports = ['49111:49111', '5002:49112', 8000]
    health_check = appinfo.HealthCheck()
    health_check.enable_health_check = False
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='vm',
        vm_settings=vm_settings,
        threadsafe=False,
        manual_scaling=manual_scaling,
        health_check=health_check,
        network=network)

    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')
    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual(os.path.realpath('/appdir/app.yaml'), config.config_path)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('dev', config.partition)
    self.assertEqual('module1', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'module1:1\.\d+')
    self.assertEqual('vm', config.runtime)
    self.assertEqual(vm_settings['vm_runtime'], config.effective_runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(manual_scaling, config.manual_scaling_config)
    self.assertFalse(config.is_automatic_scaling)
    self.assertFalse(config.is_basic_scaling)
    self.assertTrue(config.is_manual_scaling)
    self.assertEqual(config.instance_class,
                     constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS)
    self.assertEqual(
        config.memory_limit,
        constants.INSTANCE_CLASS_MEMORY_LIMIT.get(
            constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS))
    self.assertEqual({'/appdir/app.yaml': 10}, config._mtimes)
    self.assertEqual(info.health_check, config.health_check)

  def test_vm_no_version(self):
    manual_scaling = appinfo.ManualScaling()
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        runtime='vm',
        threadsafe=False,
        manual_scaling=manual_scaling,
    )

    with mock.patch.object(appinfo_includes, 'ParseAndReturnIncludePaths', return_value=(info, [])), mock.patch.object(os.path, 'getmtime', return_value=10) as getmtime_mock, mock.patch.object(application_configuration, 'generate_version_id', return_value='generated-version'):
      config = application_configuration.ModuleConfiguration('/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')

    self.assertEqual(config.major_version, 'generated-version')

  def test_vm_health_check_taken_into_account(self):
    manual_scaling = appinfo.ManualScaling()
    vm_settings = appinfo.VmSettings()
    vm_settings['vm_runtime'] = 'myawesomeruntime'
    vm_settings['forwarded_ports'] = '49111:49111,5002:49112,8000'
    vm_health_check = appinfo.VmHealthCheck(enable_health_check=False)
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='vm',
        vm_settings=vm_settings,
        threadsafe=False,
        manual_scaling=manual_scaling,
        vm_health_check=vm_health_check)

    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')

    getmtime_mock.assert_called_with('/appdir/app.yaml')
    # tests if it is not overriden from the defaults of health_check
    self.assertIs(config.health_check.enable_health_check, False)

  def test_set_health_check_defaults(self):
    # Pass nothing in.
    self.assertEqual(_DEFAULT_HEALTH_CHECK,
                     application_configuration._set_health_check_defaults(None))

    # Pass in an empty object.
    self.assertEqual(
        _DEFAULT_HEALTH_CHECK,
        application_configuration._set_health_check_defaults(
            appinfo.HealthCheck()))

    # Override some.
    health_check = appinfo.HealthCheck(restart_threshold=7, healthy_threshold=4)
    defaults_set = application_configuration._set_health_check_defaults(
        health_check)

    self.assertEqual(defaults_set.enable_health_check,
                     _DEFAULT_HEALTH_CHECK.enable_health_check)
    self.assertEqual(defaults_set.check_interval_sec,
                     _DEFAULT_HEALTH_CHECK.check_interval_sec)
    self.assertEqual(defaults_set.timeout_sec,
                     _DEFAULT_HEALTH_CHECK.timeout_sec)
    self.assertEqual(defaults_set.unhealthy_threshold,
                     _DEFAULT_HEALTH_CHECK.unhealthy_threshold)
    self.assertEqual(defaults_set.healthy_threshold, 4)
    self.assertEqual(defaults_set.restart_threshold, 7)
    self.assertEqual(defaults_set.host, _DEFAULT_HEALTH_CHECK.host)

  def test_override_app_id(self):
    info = appinfo.AppInfoExternal(
        application='ignored-app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False)

    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', side_effect=[10, 20, 20]) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml', 'overriding-app')
        self.assertEqual('overriding-app', config.application_external_name)
        self.assertEqual('dev~overriding-app', config.application)
        config.check_for_updates()
        self.assertEqual('overriding-app', config.application_external_name)
        self.assertEqual('dev~overriding-app', config.application)

    getmtime_mock.assert_has_calls([mock.call('/appdir/app.yaml')] * 3)

  def test_override_runtime(self):
    info = appinfo.AppInfoExternal(
        application='ignored-app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False)
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', side_effect=[10, 20, 20]) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml', runtime='python25')
        self.assertEqual('python25', config.runtime)
        config.check_for_updates()
        self.assertEqual('python25', config.runtime)

    getmtime_mock.assert_has_calls([mock.call('/appdir/app.yaml')] * 3)

  def test_override_and_add_environment_variables(self):
    info = appinfo.AppInfoExternal(
        application='ignored-app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False,
        env_variables=appinfo.EnvironmentVariables(**{
            'foo1': 'bar1',
            'foo2': 'old_var'
        }))
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', side_effect=[10, 20, 20]) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml', env_variables={
                'foo2': 'bar2',
                'foo3': 'bar3'
            })

        self.assertEqual({
            'foo1': 'bar1',
            'foo2': 'bar2',
            'foo3': 'bar3'
        }, config.env_variables)
        config.check_for_updates()

    getmtime_mock.assert_has_calls([mock.call('/appdir/app.yaml')] * 3)
    self.assertEqual(getmtime_mock.call_count, 3)

    self.assertEqual({
        'foo1': 'bar1',
        'foo2': 'bar2',
        'foo3': 'bar3'
    }, config.env_variables)
    config.check_for_updates()
    self.assertEqual({
        'foo1': 'bar1',
        'foo2': 'bar2',
        'foo3': 'bar3'
    }, config.env_variables)

  def test_check_for_updates_unchanged_mtime(self):
    info = appinfo.AppInfoExternal(
        application='app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False)
    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(
          os.path, 'getmtime', return_value=10) as getmtime_mock:
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        self.assertSequenceEqual(set(), config.check_for_updates())

    getmtime_mock.assert_has_calls([mock.call('/appdir/app.yaml')] * 2)

  def test_check_for_updates_with_includes(self):
    info = appinfo.AppInfoExternal(
        application='app',
        module='default',
        version='version',
        runtime='python27',
        includes=['/appdir/include.yaml'],
        threadsafe=False)

    class FakeGetmtime(object):

      def __init__(self):
        self._include_yaml_counter = 0

      def __call__(self, path):
        if path == '/appdir/app.yaml':
          return 10
        if path == '/appdir/include.yaml':
          self._include_yaml_counter += 1
          if self._include_yaml_counter == 1:
            return 10
          else:
            return 11
          raise ValueError('Unxpected path %s' % path)

    with mock.patch.object(
        appinfo_includes,
        'ParseAndReturnIncludePaths',
        return_value=(info, ['/appdir/include.yaml'])):
      with mock.patch.object(os.path, 'getmtime', side_effect=FakeGetmtime()):
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        self.assertEqual({
            '/appdir/app.yaml': 10,
            '/appdir/include.yaml': 10
        }, config._mtimes)
        config._mtimes = collections.OrderedDict([('/appdir/app.yaml', 10),
                                                  ('/appdir/include.yaml', 10)])
        self.assertSequenceEqual(set(), config.check_for_updates())
        self.assertEqual({
            '/appdir/app.yaml': 10,
            '/appdir/include.yaml': 11
        }, config._mtimes)

  def test_check_for_updates_no_changes(self):
    info = appinfo.AppInfoExternal(
        application='app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False)

    with mock.patch.object(
        appinfo_includes, 'ParseAndReturnIncludePaths',
        return_value=(info, [])):
      with mock.patch.object(os.path, 'getmtime', side_effect=[10, 11, 11, 11]):
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        self.assertSequenceEqual(set(), config.check_for_updates())
        self.assertEqual({'/appdir/app.yaml': 11}, config._mtimes)

  def test_check_for_updates_immutable_changes(self):
    automatic_scaling1 = appinfo.AutomaticScaling(
        min_pending_latency='0.1s',
        max_pending_latency='1.0s',
        min_idle_instances=1,
        max_idle_instances=2)
    info1 = appinfo.AppInfoExternal(
        application='app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False,
        automatic_scaling=automatic_scaling1)

    info2 = appinfo.AppInfoExternal(
        application='app2',
        module='default2',
        version='version2',
        runtime='python',
        threadsafe=True,
        automatic_scaling=appinfo.AutomaticScaling(
            min_pending_latency='1.0s',
            max_pending_latency='2.0s',
            min_idle_instances=1,
            max_idle_instances=2))

    with mock.patch.object(
        appinfo_includes,
        'ParseAndReturnIncludePaths',
        side_effect=[(info1, []), (info2, [])]):
      with mock.patch.object(os.path, 'getmtime', side_effect=[10, 11, 11]):
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        self.assertSequenceEqual(set(), config.check_for_updates())

    self.assertEqual('dev~app', config.application)
    self.assertEqual('default', config.module_name)
    self.assertEqual('version', config.major_version)
    self.assertRegexpMatches(config.version_id, r'^version\.\d+$')
    self.assertEqual('python27', config.runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(automatic_scaling1, config.automatic_scaling_config)

  def test_check_for_updates_mutable_changes(self):
    info1 = appinfo.AppInfoExternal(
        application='app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False,
        libraries=[appinfo.Library(name='django', version='latest')],
        skip_files='.*',
        handlers=[],
        inbound_services=['warmup'],
        env_variables=appinfo.EnvironmentVariables(),
        error_handlers=[appinfo.ErrorHandlers(file='error.html')],
    )
    info2 = appinfo.AppInfoExternal(
        application='app',
        module='default',
        version='version',
        runtime='python27',
        threadsafe=False,
        entrypoint='exec gunicorn -b :${PORT} main:app',
        libraries=[appinfo.Library(name='jinja2', version='latest')],
        skip_files=r'.*\.py',
        handlers=[appinfo.URLMap()],
        inbound_services=[],
    )

    with mock.patch.object(
        appinfo_includes,
        'ParseAndReturnIncludePaths',
        side_effect=[(info1, []), (info2, [])]):
      with mock.patch.object(os.path, 'getmtime', side_effect=[10, 11, 11]):
        config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        self.assertSequenceEqual(
            set([
                application_configuration.NORMALIZED_LIBRARIES_CHANGED,
                application_configuration.SKIP_FILES_CHANGED,
                application_configuration.HANDLERS_CHANGED,
                application_configuration.INBOUND_SERVICES_CHANGED,
                application_configuration.ENV_VARIABLES_CHANGED,
                application_configuration.ERROR_HANDLERS_CHANGED,
                application_configuration.ENTRYPOINT_ADDED
            ]), config.check_for_updates())

    self.assertEqual(info2.GetNormalizedLibraries(),
                     config.normalized_libraries)
    self.assertEqual(info2.skip_files, config.skip_files)
    self.assertEqual(info2.error_handlers, config.error_handlers)
    self.assertEqual(info2.handlers, config.handlers)
    self.assertEqual(info2.inbound_services, config.inbound_services)
    self.assertEqual(info2.env_variables, config.env_variables)
    self.assertEqual(info2.entrypoint, config.entrypoint)


class TestBackendsConfiguration(unittest.TestCase):

  def test_good_configuration(self):
    static_backend_entry = backendinfo.BackendEntry(name='static')
    dynamic_backend_entry = backendinfo.BackendEntry(name='dynamic')
    backend_info = backendinfo.BackendInfoExternal(
        backends=[static_backend_entry, dynamic_backend_entry])
    module_config = object()
    static_configuration = object()
    dynamic_configuration = object()

    def backend_configuration_effects(unused_module_config, unused_arg,
                                      backend_entry):
      if backend_entry == static_backend_entry:
        return static_configuration
      elif backend_entry == dynamic_backend_entry:
        return dynamic_configuration
      else:
        raise ValueError('Unrecognized backend entry')

    with mock.patch.object(application_configuration, 'ModuleConfiguration',
                           return_value=module_config), mock.patch.object(application_configuration, 'BackendConfiguration',
                          side_effect=backend_configuration_effects), mock.patch.object(application_configuration.BackendsConfiguration,
                          '_parse_configuration', return_value=backend_info):
      config = application_configuration.BackendsConfiguration(
          '/appdir/app.yaml', '/appdir/backends.yaml')
      six.assertCountEqual(self, [static_configuration, dynamic_configuration],
                           config.get_backend_configurations())

  def test_no_backends(self):
    backend_info = backendinfo.BackendInfoExternal()
    module_config = object()

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      with mock.patch.object(
          application_configuration.BackendsConfiguration,
          '_parse_configuration',
          return_value=backend_info):
        config = application_configuration.BackendsConfiguration(
            '/appdir/app.yaml', '/appdir/backends.yaml')
        self.assertEqual([], config.get_backend_configurations())

  def test_check_for_changes(self):
    static_backend_entry = backendinfo.BackendEntry(name='static')
    dynamic_backend_entry = backendinfo.BackendEntry(name='dynamic')
    backend_info = backendinfo.BackendInfoExternal(
        backends=[static_backend_entry, dynamic_backend_entry])
    module_config = mock.Mock(
        spec=application_configuration.ModuleConfiguration)
    module_config.check_for_updates.side_effect = (set(), set([1]), set([2]),
                                                   set())

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      with mock.patch.object(
          application_configuration.BackendsConfiguration,
          '_parse_configuration',
          return_value=backend_info):
        config = application_configuration.BackendsConfiguration(
            '/appdir/app.yaml', '/appdir/backends.yaml')
        self.assertEqual(set(), config.check_for_updates('dynamic'))
        self.assertEqual(set([1]), config.check_for_updates('static'))
        self.assertEqual(set([1, 2]), config.check_for_updates('dynamic'))
        self.assertEqual(set([2]), config.check_for_updates('static'))


class TestDispatchConfiguration(unittest.TestCase):

  def test_good_configuration(self):
    info = dispatchinfo.DispatchInfoExternal(
        application='appid',
        dispatch=[
            dispatchinfo.DispatchEntry(url='*/path', module='foo'),
            dispatchinfo.DispatchEntry(url='domain.com/path', module='bar'),
            dispatchinfo.DispatchEntry(url='*/path/*', module='baz'),
            dispatchinfo.DispatchEntry(url='*.domain.com/path/*', module='foo'),
        ])

    with mock.patch.object(
        application_configuration.DispatchConfiguration,
        '_parse_configuration',
        return_value=info):
      with mock.patch.object(os.path, 'getmtime', return_value=123.456):
        config = application_configuration.DispatchConfiguration(
            '/appdir/dispatch.yaml')

    self.assertEqual(123.456, config._mtime)
    self.assertEqual(2, len(config.dispatch))
    self.assertEqual(
        vars(dispatchinfo.ParsedURL('*/path')), vars(config.dispatch[0][0]))
    self.assertEqual('foo', config.dispatch[0][1])
    self.assertEqual(
        vars(dispatchinfo.ParsedURL('*/path/*')), vars(config.dispatch[1][0]))
    self.assertEqual('baz', config.dispatch[1][1])

  def test_check_for_updates_no_modification(self):
    info = dispatchinfo.DispatchInfoExternal(application='appid', dispatch=[])
    with mock.patch.object(
        application_configuration.DispatchConfiguration,
        '_parse_configuration',
        return_value=info):
      with mock.patch.object(
          os.path, 'getmtime', return_value=123.456) as mock_getmtime:
        config = application_configuration.DispatchConfiguration(
            '/appdir/dispatch.yaml')
        config.check_for_updates()
    self.assertEqual(mock_getmtime.call_count, 2)

  def test_check_for_updates_with_invalid_modification(self):
    info = dispatchinfo.DispatchInfoExternal(
        application='appid',
        dispatch=[
            dispatchinfo.DispatchEntry(url='*/path', module='bar'),
        ])

    with mock.patch.object(
        application_configuration.DispatchConfiguration,
        '_parse_configuration',
        side_effect=[info, Exception()]):
      with mock.patch.object(
          os.path, 'getmtime', return_value=123.456) as mock_getmtime:
        config = application_configuration.DispatchConfiguration(
            '/appdir/dispatch.yaml')
        self.assertEqual('bar', config.dispatch[0][1])
        config.check_for_updates()

    self.assertEqual(mock_getmtime.call_count, 2)
    self.assertEqual('bar', config.dispatch[0][1])

  def test_check_for_updates_with_modification(self):
    info = dispatchinfo.DispatchInfoExternal(
        application='appid',
        dispatch=[
            dispatchinfo.DispatchEntry(url='*/path', module='bar'),
        ])
    new_info = dispatchinfo.DispatchInfoExternal(
        application='appid',
        dispatch=[
            dispatchinfo.DispatchEntry(url='*/path', module='foo'),
        ])

    with mock.patch.object(
        application_configuration.DispatchConfiguration,
        '_parse_configuration',
        side_effect=[info, new_info]):
      with mock.patch.object(
          os.path, 'getmtime', side_effect=[123.456, 124.456]):
        config = application_configuration.DispatchConfiguration(
            '/appdir/dispatch.yaml')
        self.assertEqual('bar', config.dispatch[0][1])
        config.check_for_updates()
        self.assertEqual('foo', config.dispatch[0][1])


class TestBackendConfiguration(unittest.TestCase):

  def test_good_configuration(self):
    automatic_scaling = appinfo.AutomaticScaling(
        min_pending_latency='1.0s',
        max_pending_latency='2.0s',
        min_idle_instances=1,
        max_idle_instances=2)
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap()]
    env_variables = appinfo.EnvironmentVariables()
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        env='1',
        version='1',
        runtime='python27',
        threadsafe=False,
        automatic_scaling=automatic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=env_variables,
        default_expiration='4d 3h',
    )
    backend_entry = backendinfo.BackendEntry(
        name='static', instances='3', options='public')

    with mock.patch.object(
        application_configuration.ModuleConfiguration,
        '_parse_configuration',
        return_value=(info, ['/appdir/app.yaml'])):
      with mock.patch.object(os.path, 'getmtime', return_value=10):
        module_config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        config = application_configuration.BackendConfiguration(
            module_config, None, backend_entry)

    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('dev', config.partition)
    self.assertEqual('1', config.env)
    self.assertEqual('static', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'static:1\.\d+')
    self.assertEqual('python27', config.runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(None, config.automatic_scaling_config)
    self.assertEqual(None, config.basic_scaling_config)
    self.assertEqual(
        appinfo.ManualScaling(instances='3'), config.manual_scaling_config)
    self.assertEqual(info.GetNormalizedLibraries(), config.normalized_libraries)
    self.assertEqual(r'\*.gif', config.skip_files)
    self.assertEqual(error_handlers, config.error_handlers)
    self.assertEqual(handlers, config.handlers)
    self.assertEqual(['warmup'], config.inbound_services)
    self.assertEqual(env_variables, config.env_variables)

    whitelist_fields = [
        'module_name', 'version_id', 'automatic_scaling_config',
        'manual_scaling_config', 'basic_scaling_config', 'is_backend',
        'minor_version', 'instance_class', 'memory_limit',
        'is_automatic_scaling', 'is_manual_scaling', 'is_basic_scaling'
    ]
    # Check that all public attributes and methods in a ModuleConfiguration
    # exist in a BackendConfiguration.
    for field in dir(module_config):
      if not field.startswith('_'):
        self.assertTrue(hasattr(config, field), 'Missing field: %s' % field)
        value = getattr(module_config, field)
        if field not in whitelist_fields and not callable(value):
          # Check that the attributes other than those in the whitelist have
          # equal values in the BackendConfiguration to the ModuleConfiguration
          # from which it inherits.
          self.assertEqual(value, getattr(config, field))

  def test_vm_app_yaml_configuration(self):
    automatic_scaling = appinfo.AutomaticScaling(
        min_pending_latency='1.0s',
        max_pending_latency='2.0s',
        min_idle_instances=1,
        max_idle_instances=2)
    beta_settings = appinfo.BetaSettings()
    beta_settings['vm_runtime'] = 'myawesomeruntime'
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='vm',
        beta_settings=beta_settings,
        threadsafe=False,
        automatic_scaling=automatic_scaling,
    )
    backend_entry = backendinfo.BackendEntry(
        name='static', instances='3', options='public')

    with mock.patch.object(
        application_configuration.ModuleConfiguration,
        '_parse_configuration',
        return_value=(info, ['/appdir/app.yaml'])):
      with mock.patch.object(os.path, 'getmtime', return_value=10):
        module_config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        config = application_configuration.BackendConfiguration(
            module_config, None, backend_entry)

    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('app', config.application_external_name)
    self.assertEqual('dev', config.partition)
    self.assertEqual('static', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'static:1\.\d+')
    self.assertEqual('vm', config.runtime)
    self.assertEqual(beta_settings['vm_runtime'], config.effective_runtime)
    self.assertFalse(config.threadsafe)
    # Resident backends are assigned manual scaling.
    self.assertEqual(None, config.automatic_scaling_config)
    self.assertEqual(None, config.basic_scaling_config)
    self.assertEqual(
        appinfo.ManualScaling(instances='3'), config.manual_scaling_config)
    self.assertFalse(config.is_automatic_scaling)
    self.assertFalse(config.is_basic_scaling)
    self.assertTrue(config.is_manual_scaling)
    self.assertEqual(config.instance_class,
                     constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS)
    self.assertEqual(
        config.memory_limit,
        constants.INSTANCE_CLASS_MEMORY_LIMIT.get(
            constants.DEFAULT_MANUAL_SCALING_INSTANCE_CLASS))

  def test_good_configuration_dynamic_scaling(self):
    automatic_scaling = appinfo.AutomaticScaling(
        min_pending_latency='1.0s',
        max_pending_latency='2.0s',
        min_idle_instances=1,
        max_idle_instances=2)
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap()]
    env_variables = appinfo.EnvironmentVariables()
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='python27',
        threadsafe=False,
        automatic_scaling=automatic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=env_variables,
    )
    backend_entry = backendinfo.BackendEntry(
        name='dynamic',
        instances='3',
        options='public, dynamic',
        start='handler')

    with mock.patch.object(
        application_configuration.ModuleConfiguration,
        '_parse_configuration',
        return_value=(info, ['/appdir/app.yaml'])):
      with mock.patch.object(os.path, 'getmtime', return_value=10):
        module_config = application_configuration.ModuleConfiguration(
            '/appdir/app.yaml')
        config = application_configuration.BackendConfiguration(
            module_config, None, backend_entry)

    self.assertEqual(os.path.realpath('/appdir'), config.application_root)
    self.assertEqual('dev~app', config.application)
    self.assertEqual('dynamic', config.module_name)
    self.assertEqual('1', config.major_version)
    self.assertRegexpMatches(config.version_id, r'dynamic:1\.\d+')
    self.assertEqual('python27', config.runtime)
    self.assertFalse(config.threadsafe)
    self.assertEqual(None, config.automatic_scaling_config)
    self.assertEqual(None, config.manual_scaling_config)
    self.assertEqual(
        appinfo.BasicScaling(max_instances='3'), config.basic_scaling_config)
    self.assertFalse(config.is_automatic_scaling)
    self.assertTrue(config.is_basic_scaling)
    self.assertFalse(config.is_manual_scaling)
    self.assertEqual(config.instance_class,
                     constants.DEFAULT_AUTO_SCALING_INSTANCE_CLASS)
    self.assertEqual(
        config.memory_limit,
        constants.INSTANCE_CLASS_MEMORY_LIMIT.get(
            constants.DEFAULT_AUTO_SCALING_INSTANCE_CLASS))
    self.assertEqual(info.GetNormalizedLibraries(), config.normalized_libraries)
    self.assertEqual(r'\*.gif', config.skip_files)
    self.assertEqual(error_handlers, config.error_handlers)
    start_handler = appinfo.URLMap(
        url='/_ah/start', script=backend_entry.start, login='admin')
    self.assertEqual([start_handler] + handlers, config.handlers)
    self.assertEqual(['warmup'], config.inbound_services)
    self.assertEqual(env_variables, config.env_variables)

  def test_check_for_changes(self):
    backends_config = mock.Mock(
        spec=application_configuration.BackendsConfiguration)
    config = application_configuration.BackendConfiguration(
        None, backends_config, backendinfo.BackendEntry(name='backend'))
    changes = object()
    backends_config.check_for_updates.side_effect = ([], changes)
    minor_version = config.minor_version

    self.assertEqual([], config.check_for_updates())
    self.assertEqual(minor_version, config.minor_version)
    self.assertEqual(changes, config.check_for_updates())
    self.assertNotEqual(minor_version, config.minor_version)
    backends_config.check_for_updates.assert_has_calls([mock.call('backend')] *
                                                       2)
    self.assertEqual(backends_config.check_for_updates.call_count, 2)


class ModuleConfigurationStub(object):

  def __init__(self, application='myapp', module_name='module'):
    self.application = application
    self.module_name = module_name


class DispatchConfigurationStub(object):

  def __init__(self, dispatch):
    self.dispatch = dispatch


class TestApplicationConfiguration(unittest.TestCase):
  """Tests for application_configuration.ApplicationConfiguration."""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp(dir=os.getenv('TEST_TMPDIR'))

  def tearDown(self):
    shutil.rmtree(self.tmpdir)

  def _make_file_hierarchy(self, filenames):
    absnames = []
    for filename in filenames:
      absname = os.path.normpath(
          six.ensure_str(self.tmpdir) + '/' + six.ensure_str(filename))
      absnames += [absname]
      dirname = os.path.dirname(absname)
      if not os.path.exists(dirname):
        os.makedirs(dirname)
      open(absname, 'w').close()
    return absnames

  def test_yaml_files(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/other.yaml'])

    module_config1 = ModuleConfigurationStub()
    module_config2 = ModuleConfigurationStub(module_name='other')

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        side_effect=(module_config1,
                     module_config2)) as mock_module_configuration:
      config = application_configuration.ApplicationConfiguration(absnames)

    mock_module_configuration.assert_has_calls([
        mock.call(absnames[0], None, None, None),
        mock.call(absnames[1], None, None, None)
    ])
    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config1, module_config2], config.modules)

  def test_yaml_files_with_different_app_ids(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/other.yaml'])

    module_config1 = ModuleConfigurationStub()
    module_config2 = ModuleConfigurationStub(
        application='other_app', module_name='other')

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        side_effect=(module_config1,
                     module_config2)) as mock_module_configuration:
      with self.assertRaises(errors.InvalidAppConfigError):
        application_configuration.ApplicationConfiguration(absnames)

    mock_module_configuration.assert_has_calls([
        mock.call(absnames[0], None, None, None),
        mock.call(absnames[1], None, None, None)
    ])

  def test_yaml_files_with_duplicate_module_names(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/other.yaml'])

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        side_effect=(ModuleConfigurationStub(), ModuleConfigurationStub())):
      with self.assertRaises(errors.InvalidAppConfigError):
        application_configuration.ApplicationConfiguration(absnames)

  def test_directory(self):
    absnames = self._make_file_hierarchy(['appdir/app.yaml'])

    module_config = ModuleConfigurationStub()
    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      config = application_configuration.ApplicationConfiguration(
          [os.path.dirname(absnames[0])])

    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config], config.modules)

  def test_directory_and_module(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'otherdir/mymodule.yaml'])

    app_yaml_config = ModuleConfigurationStub()
    my_module_config = ModuleConfigurationStub(module_name='my_module')

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        side_effect=(app_yaml_config, my_module_config)):
      config = application_configuration.ApplicationConfiguration(
          [os.path.dirname(absnames[0]), absnames[1]])

    self.assertSequenceEqual([app_yaml_config, my_module_config],
                             config.modules)

  def test_directory_app_yml_only(self):
    absnames = self._make_file_hierarchy(['appdir/app.yml'])

    module_config = ModuleConfigurationStub()

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      config = application_configuration.ApplicationConfiguration(
          [os.path.dirname(absnames[0])])

    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config], config.modules)

  def test_directory_app_yaml_and_app_yml(self):
    absnames = self._make_file_hierarchy(['appdir/app.yaml', 'appdir/app.yml'])

    with self.assertRaises(errors.InvalidAppConfigError):
      application_configuration.ApplicationConfiguration(
          [os.path.dirname(absnames[0])])

  def test_directory_no_app_yamls(self):
    absnames = self._make_file_hierarchy(['appdir/somethingelse.yaml'])

    with self.assertRaises(errors.AppConfigNotFoundError):
      application_configuration.ApplicationConfiguration(
          [os.path.dirname(absnames[0])])

  def test_directory_no_app_yamls_or_web_inf(self):
    absnames = self._make_file_hierarchy(['appdir/somethingelse.yaml'])

    with _java_temporarily_supported():
      with self.assertRaises(errors.AppConfigNotFoundError):
        application_configuration.ApplicationConfiguration(
            [os.path.dirname(absnames[0])])

  def test_app_yaml(self):
    absnames = self._make_file_hierarchy(['appdir/app.yaml'])

    module_config = ModuleConfigurationStub()

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      config = application_configuration.ApplicationConfiguration(absnames)

    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config], config.modules)

  def test_directory_with_backends_yaml(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/backends.yaml'])

    module_config = ModuleConfigurationStub()
    backend_config = ModuleConfigurationStub(module_name='backend')
    backends_config = mock.Mock(
        spec=application_configuration.BackendsConfiguration)
    backends_config.get_backend_configurations.return_value = [backend_config]

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      with mock.patch.object(
          application_configuration,
          'BackendsConfiguration',
          return_value=backends_config):
        config = application_configuration.ApplicationConfiguration(
            [os.path.dirname(absnames[0])])

    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config, backend_config], config.modules)

  def test_yaml_files_with_backends_yaml(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/backends.yaml'])

    module_config = ModuleConfigurationStub()
    backend_config = ModuleConfigurationStub(module_name='backend')
    backends_config = mock.Mock(
        spec=application_configuration.BackendsConfiguration)
    backends_config.get_backend_configurations.return_value = [backend_config]

    with mock.patch.object(
        application_configuration,
        'ModuleConfiguration',
        return_value=module_config):
      with mock.patch.object(
          application_configuration,
          'BackendsConfiguration',
          return_value=backends_config) as backend_config_mock:
        config = application_configuration.ApplicationConfiguration(absnames)

    backend_config_mock.assert_called_with(absnames[0], absnames[1], None, None,
                                           None)
    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config, backend_config], config.modules)

  def test_yaml_files_with_backends_and_dispatch_yaml(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/backends.yaml', 'appdir/dispatch.yaml'])

    module_config = ModuleConfigurationStub(module_name='default')
    backend_config = ModuleConfigurationStub(module_name='backend')
    backends_config = mock.Mock(
        spec=application_configuration.BackendsConfiguration)
    backends_config.get_backend_configurations.return_value = [backend_config]
    dispatch_config = DispatchConfigurationStub([(None, 'default'),
                                                 (None, 'backend')])

    with mock.patch.object(application_configuration, 'ModuleConfiguration',
                           return_value=module_config), mock.patch.object(application_configuration, 'BackendsConfiguration',
                          return_value=backends_config), mock.patch.object(application_configuration, 'DispatchConfiguration',
                          return_value=dispatch_config) as dispatch_mock:
      config = application_configuration.ApplicationConfiguration(absnames)

    dispatch_mock.assert_called_with(absnames[2])
    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config, backend_config], config.modules)
    self.assertEqual(dispatch_config, config.dispatch)

  def test_yaml_files_dispatch_yaml_and_no_default_module(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/dispatch.yaml'])

    module_config = ModuleConfigurationStub(module_name='not-default')
    dispatch_config = DispatchConfigurationStub([(None, 'default')])

    with mock.patch.object(
        application_configuration, 'ModuleConfiguration',
        return_value=module_config), mock.patch.object(application_configuration, 'DispatchConfiguration',
                          return_value=dispatch_config) as dispatch_mock, self.assertRaises(errors.InvalidAppConfigError):
      application_configuration.ApplicationConfiguration(absnames)

    dispatch_mock.assert_called_with(absnames[1])

  def test_yaml_files_dispatch_yaml_and_missing_dispatch_target(self):
    absnames = self._make_file_hierarchy(
        ['appdir/app.yaml', 'appdir/dispatch.yaml'])

    module_config = ModuleConfigurationStub(module_name='default')
    dispatch_config = DispatchConfigurationStub([(None, 'default'),
                                                 (None, 'fake-module')])

    with mock.patch.object(application_configuration, 'ModuleConfiguration',
                           return_value=module_config), mock.patch.object(application_configuration, 'DispatchConfiguration',
                           return_value=dispatch_config), self.assertRaises(errors.InvalidAppConfigError):
      application_configuration.ApplicationConfiguration(absnames)

  def test_directory_web_inf(self):
    absnames = self._make_file_hierarchy(
        ['appdir/WEB-INF/appengine-web.xml', 'appdir/WEB-INF/web.xml'])
    appdir = os.path.dirname(os.path.dirname(absnames[0]))

    module_config = ModuleConfigurationStub(module_name='default')

    with _java_temporarily_supported():
      with mock.patch.object(
          application_configuration,
          'ModuleConfiguration',
          return_value=module_config):
        config = application_configuration.ApplicationConfiguration([appdir])

    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module_config], config.modules)

  def test_directory_web_inf_missing_appengine_xml(self):
    absnames = self._make_file_hierarchy(['appdir/WEB-INF/web.xml'])
    appdir = os.path.dirname(os.path.dirname(absnames[0]))

    with _java_temporarily_supported():
      self.assertRaises(errors.AppConfigNotFoundError,
                        application_configuration.ApplicationConfiguration,
                        [appdir])

  def test_directory_web_inf_missing_web_xml(self):
    absnames = self._make_file_hierarchy(['appdir/WEB-INF/appengine-web.xml'])
    appdir = os.path.dirname(os.path.dirname(absnames[0]))

    with _java_temporarily_supported():
      self.assertRaises(errors.AppConfigNotFoundError,
                        application_configuration.ApplicationConfiguration,
                        [appdir])

  def test_config_with_yaml_and_xml(self):
    absnames = self._make_file_hierarchy([
        'module1/app.yaml', 'module1/dispatch.yaml',
        'module2/WEB-INF/appengine-web.xml', 'module2/WEB-INF/web.xml'
    ])
    app_yaml = absnames[0]
    dispatch_yaml = absnames[1]
    appengine_web_xml = absnames[2]
    module2 = os.path.dirname(os.path.dirname(appengine_web_xml))

    module1_config = ModuleConfigurationStub(module_name='default')
    dispatch_config = DispatchConfigurationStub([(None, 'default'),
                                                 (None, 'module2')])
    module2_config = ModuleConfigurationStub(module_name='module2')

    with mock.patch.object(application_configuration, 'ModuleConfiguration',
                           side_effect=[module1_config, module2_config]) as module_config_mock, mock.patch.object(application_configuration, 'DispatchConfiguration',
                           return_value=dispatch_config) as dispatch_mock, _java_temporarily_supported():
      config = application_configuration.ApplicationConfiguration(
          [app_yaml, dispatch_yaml, module2])

    dispatch_mock.assert_called_with(dispatch_yaml)
    module_config_mock.assert_has_calls([
        mock.call(app_yaml, None, None, None),
        mock.call(appengine_web_xml, None, None, None)
    ])
    self.assertEqual('myapp', config.app_id)
    self.assertSequenceEqual([module1_config, module2_config], config.modules)
    self.assertEqual(dispatch_config, config.dispatch)


class GenerateVersionIdTest(unittest.TestCase):
  """Tests the GenerateVersionId function."""

  def test_generate_version_id(self):
    datetime_getter = lambda: datetime.datetime(2014, 9, 18, 17, 31, 45, 92949)
    generated_version = application_configuration.generate_version_id(
        datetime_getter)
    self.assertEqual(generated_version, '20140918t173145')


if __name__ == '__main__':
  unittest.main()
