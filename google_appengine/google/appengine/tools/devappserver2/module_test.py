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
"""Tests for google.apphosting.tools.devappserver2.module."""

import functools
import logging
import os
import re
import time

# concurrent.futures must appear after import google. Somehow, the linter
# expects it to come before the linter.
# pylint: disable=g-bad-import-order

import google
from concurrent import futures
import mox
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
from google.appengine.api import appinfo
from google.appengine.api import request_info

from google.appengine.tools.devappserver2 import application_configuration
from google.appengine.tools.devappserver2 import constants
from google.appengine.tools.devappserver2 import dispatcher
from google.appengine.tools.devappserver2 import errors
from google.appengine.tools.devappserver2 import instance
from google.appengine.tools.devappserver2 import metrics
from google.appengine.tools.devappserver2 import module
from google.appengine.tools.devappserver2 import runtime_config_pb2
from google.appengine.tools.devappserver2 import start_response_utils
from google.appengine.tools.devappserver2 import stub_testing
from google.appengine.tools.devappserver2 import wsgi_server
from google.appengine.tools.devappserver2.go import gaego as gaego_application
from google.appengine.tools.devappserver2.go import instance_factory as go_factory
from google.testing.pybase import googletest
from google.testing.pybase import parameterized


class ModuleConfigurationStub(object):

  def __init__(self,
               application_root='/root',
               application='app',
               module_name='default',
               automatic_scaling=appinfo.AutomaticScaling(),
               version='version',
               runtime='python312',
               env='1',
               effective_runtime='',
               threadsafe=False,
               skip_files='',
               inbound_services=['warmup'],
               handlers=[appinfo.URLMap(url=r'/python-(.*)', script=r'\1.py')],
               normalized_libraries=None,
               env_variables=None,
               manual_scaling=None,
               basic_scaling=None,
               application_external_name='app',
               default_expiration=None):
    self.application_root = application_root
    self.application = application
    self.module_name = module_name
    self.automatic_scaling_config = automatic_scaling
    self.manual_scaling_config = manual_scaling
    self.basic_scaling_config = basic_scaling
    self.major_version = version
    self.runtime = runtime
    self.env = env
    self.effective_runtime = effective_runtime
    self.threadsafe = threadsafe
    self.skip_files = skip_files
    self.inbound_services = inbound_services
    self.handlers = handlers
    self.normalized_libraries = normalized_libraries or []
    self.env_variables = env_variables or []
    self.version_id = '%s:%s.%s' % (module_name, version, '12345')
    self.is_backend = False
    self.application_external_name = application_external_name
    self.default_expiration = default_expiration

  def check_for_updates(self):
    return set()


class InstanceFactoryFacade(instance.InstanceFactory):
  START_URL_MAP = appinfo.URLMap(
      url='/_ah/start', script='ignored', login='admin')
  WARMUP_URL_MAP = appinfo.URLMap(
      url='/_ah/warmup', script='ignored', login='admin')


class NoOpInstanceFactoryFacade(instance.InstanceFactory):
  START_URL_MAP = appinfo.URLMap(
      url='/_ah/start', script='ignored', login='admin')
  WARMUP_URL_MAP = appinfo.URLMap(
      url='/_ah/warmup', script='ignored', login='admin')

  def new_instance(self, instance_id, expect_ready_request=False):
    pass


class FakeInstanceFactory:
  START_URL_MAP = appinfo.URLMap(
      url='/_ah/start', script='ignored', login='admin')
  WARMUP_URL_MAP = appinfo.URLMap(
      url='/_ah/warmup', script='ignored', login='admin')

  def get_restart_directories(self):
    return []


class ModuleFacade(module.Module):

  def __init__(self,
               module_configuration=ModuleConfigurationStub(),
               instance_factory=None,
               ready=True,
               allow_skipped_files=False,
               threadsafe_override=None,
               custom_config=None,
               php_config=None,
               python_config=None,
               go_config=None,
               vm_config=None):
    self._instance_factory = instance_factory
    super(ModuleFacade, self).__init__(
        module_configuration,
        host='fakehost',
        balanced_port=0,
        api_host='localhost',
        api_port=8080,
        auth_domain='gmail.com',
        runtime_stderr_loglevel=1,
        php_config=None,
        python_config=None,
        go_config=None,
        custom_config=custom_config,
        cloud_sql_config=None,
        vm_config=vm_config,
        default_version_port=8080,
        port_registry=dispatcher.PortRegistry(),
        request_data=None,
        dispatcher=None,
        max_instances=None,
        use_mtime_file_watcher=False,
        watcher_ignore_re=None,
        automatic_restarts=True,
        allow_skipped_files=allow_skipped_files,
        threadsafe_override=threadsafe_override)
    self._ready = ready

  @property
  def ready(self):
    return self._ready

  @property
  def balanced_port(self):
    return self._balanced_port

  def _create_instance_factory(self, module_configuration):
    if self._instance_factory:
      return self._instance_factory
    return super(
        ModuleFacade, self)._create_instance_factory(module_configuration)


class NoHandlersModuleFacade(ModuleFacade):
  def  _create_url_handlers(self):
    return []


class AutoScalingModuleFacade(module.AutoScalingModule):

  def __init__(self,
               module_configuration=ModuleConfigurationStub(),
               balanced_port=0,
               instance_factory=None,
               max_instances=None,
               ready=True):
    self._instance_factory = instance_factory
    super(AutoScalingModuleFacade, self).__init__(
        module_configuration=module_configuration,
        host='fakehost',
        balanced_port=balanced_port,
        api_host='localhost',
        api_port=8080,
        auth_domain='gmail.com',
        runtime_stderr_loglevel=1,
        php_config=None,
        python_config=None,
        go_config=None,
        custom_config=None,
        cloud_sql_config=None,
        vm_config=None,
        default_version_port=8080,
        port_registry=dispatcher.PortRegistry(),
        request_data=None,
        dispatcher=None,
        max_instances=max_instances,
        use_mtime_file_watcher=False,
        watcher_ignore_re=None,
        automatic_restarts=True,
        allow_skipped_files=False,
        threadsafe_override=None)
    self._ready = ready

  @property
  def ready(self):
    return self._ready

  @property
  def balanced_port(self):
    return self._balanced_port

  def get_file_change_count(self):
    return self._file_change_count

  def _create_instance_factory(self, module_configuration):
    if self._instance_factory:
      return self._instance_factory
    return FakeInstanceFactory()


class ManualScalingModuleFacade(module.ManualScalingModule):

  def __init__(self,
               module_configuration=None,
               balanced_port=0,
               instance_factory=None,
               ready=True,
               vm_config=None):
    self._instance_factory = instance_factory
    if module_configuration is None:
      module_configuration = ModuleConfigurationStub()
    super(ManualScalingModuleFacade, self).__init__(
        module_configuration=module_configuration,
        host='fakehost',
        balanced_port=balanced_port,
        api_host='localhost',
        api_port=8080,
        auth_domain='gmail.com',
        runtime_stderr_loglevel=1,
        php_config=None,
        python_config=None,
        go_config=None,
        custom_config=None,
        cloud_sql_config=None,
        vm_config=vm_config,
        default_version_port=8080,
        port_registry=dispatcher.PortRegistry(),
        request_data=None,
        dispatcher=None,
        max_instances=None,
        use_mtime_file_watcher=False,
        watcher_ignore_re=None,
        automatic_restarts=True,
        allow_skipped_files=False,
        threadsafe_override=None)
    self._ready = ready

  @property
  def ready(self):
    return self._ready

  @property
  def balanced_port(self):
    return self._balanced_port

  def get_file_change_count(self):
    return self._file_change_count

  def _create_instance_factory(self, module_configuration):
    if self._instance_factory:
      return self._instance_factory
    return FakeInstanceFactory()


class BasicScalingModuleFacade(module.BasicScalingModule):

  def __init__(self,
               host='fakehost',
               module_configuration=ModuleConfigurationStub(),
               balanced_port=0,
               instance_factory=None,
               ready=True):
    self._instance_factory = instance_factory
    super(BasicScalingModuleFacade, self).__init__(
        module_configuration=module_configuration,
        host=host,
        balanced_port=balanced_port,
        api_host='localhost',
        api_port=8080,
        auth_domain='gmail.com',
        runtime_stderr_loglevel=1,
        php_config=None,
        python_config=None,
        go_config=None,
        custom_config=None,
        cloud_sql_config=None,
        vm_config=None,
        default_version_port=8080,
        port_registry=dispatcher.PortRegistry(),
        request_data=None,
        dispatcher=None,
        max_instances=None,
        use_mtime_file_watcher=False,
        watcher_ignore_re=None,
        automatic_restarts=True,
        allow_skipped_files=False,
        threadsafe_override=None)
    self._ready = ready

  @property
  def ready(self):
    return self._ready

  @property
  def balanced_port(self):
    return self._balanced_port

  def get_file_change_count(self):
    return self._file_change_count

  def _create_url_handlers(self):
    pass

  def _create_instance_factory(self, module_configuration):
    if self._instance_factory:
      return self._instance_factory
    return FakeInstanceFactory()


class ExternalModuleFacade(module.ExternalModule):

  def __init__(self,
               host='fakehost',
               module_configuration=ModuleConfigurationStub(),
               balanced_port=0,
               instance_factory=None,
               ready=True):
    super(ExternalModuleFacade, self).__init__(
        module_configuration=module_configuration,
        host=host,
        balanced_port=balanced_port,
        api_host='localhost',
        api_port=8080,
        auth_domain='gmail.com',
        runtime_stderr_loglevel=1,
        php_config=None,
        python_config=None,
        go_config=None,
        custom_config=None,
        cloud_sql_config=None,
        vm_config=None,
        default_version_port=8080,
        port_registry=dispatcher.PortRegistry(),
        request_data=None,
        dispatcher=None,
        max_instances=None,
        use_mtime_file_watcher=False,
        watcher_ignore_re=None,
        automatic_restarts=True,
        allow_skipped_files=False,
        threadsafe_override=None)
    if instance_factory is not None:
      self._instance_factory = instance_factory
    self._ready = ready

  @property
  def ready(self):
    return self._ready

  @property
  def balanced_port(self):
    return self._balanced_port

  def  _create_url_handlers(self):
    pass


class BuildRequestEnvironTest(stub_testing.StubTestCase):

  def setUp(self):
    super(BuildRequestEnvironTest, self).setUp()
    self.instance_factory = NoOpInstanceFactoryFacade(None, 1)
    self.module = ModuleFacade(instance_factory=self.instance_factory)

  def test_build_request_environ(self):
    expected_environ = {
        constants.FAKE_IS_ADMIN_HEADER: '1',
        'HTTP_HOST': 'fakehost:8080',
        'HTTP_HEADER': 'Value',
        'HTTP_OTHER': 'Values',
        'CONTENT_LENGTH': '4',
        'PATH_INFO': '/foo',
        'QUERY_STRING': 'bar=baz',
        'REQUEST_METHOD': 'PUT',
        'REMOTE_ADDR': '1.2.3.4',
        'SERVER_NAME': 'fakehost',
        'SERVER_PORT': '8080',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': True,
        'wsgi.multiprocess': True
    }
    environ = self.module.build_request_environ('PUT', '/foo?bar=baz',
                                                [('Header', 'Value'),
                                                 ('Other', 'Values')], 'body',
                                                '1.2.3.4', 8080)
    self.assertEqual('', environ.pop('wsgi.errors').getvalue())
    self.assertEqual(b'body', environ.pop('wsgi.input').getvalue())
    self.assertEqual(expected_environ, environ)

  def test_build_request_environ_fake_is_logged_in(self):
    expected_environ = {
        constants.FAKE_IS_ADMIN_HEADER: '1',
        constants.FAKE_LOGGED_IN_HEADER: '1',
        'HTTP_HOST': 'fakehost:8080',
        'HTTP_HEADER': 'Value',
        'HTTP_OTHER': 'Values',
        'CONTENT_LENGTH': '4',
        'PATH_INFO': '/foo',
        'QUERY_STRING': 'bar=baz',
        'REQUEST_METHOD': 'PUT',
        'REMOTE_ADDR': '1.2.3.4',
        'SERVER_NAME': 'fakehost',
        'SERVER_PORT': '8080',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': True,
        'wsgi.multiprocess': True
    }
    environ = self.module.build_request_environ(
        'PUT',
        '/foo?bar=baz', [('Header', 'Value'), ('Other', 'Values')],
        'body',
        '1.2.3.4',
        8080,
        fake_login=True)
    self.assertEqual('', environ.pop('wsgi.errors').getvalue())
    self.assertEqual(b'body', environ.pop('wsgi.input').getvalue())
    self.assertEqual(expected_environ, environ)

  def test_build_request_environ_unicode_body(self):
    expected_environ = {
        constants.FAKE_IS_ADMIN_HEADER: '1',
        'HTTP_HOST': 'fakehost',
        'HTTP_HEADER': 'Value',
        'HTTP_OTHER': 'Values',
        'CONTENT_LENGTH': '4',
        'PATH_INFO': '/foo',
        'QUERY_STRING': 'bar=baz',
        'REQUEST_METHOD': 'PUT',
        'REMOTE_ADDR': '1.2.3.4',
        'SERVER_NAME': 'fakehost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': True,
        'wsgi.multiprocess': True
    }
    environ = self.module.build_request_environ('PUT', '/foo?bar=baz',
                                                [('Header', 'Value'),
                                                 ('Other', 'Values')], u'body',
                                                '1.2.3.4', 80)
    self.assertEqual('', environ.pop('wsgi.errors').getvalue())
    self.assertEqual(b'body', environ.pop('wsgi.input').getvalue())
    self.assertEqual(expected_environ, environ)

  def test_build_request_environ_bytes_body(self):
    expected_environ = {
        constants.FAKE_IS_ADMIN_HEADER: '1',
        'HTTP_HOST': 'fakehost',
        'HTTP_HEADER': 'Value',
        'HTTP_OTHER': 'Values',
        'CONTENT_LENGTH': '4',
        'PATH_INFO': '/foo',
        'QUERY_STRING': 'bar=baz',
        'REQUEST_METHOD': 'PUT',
        'REMOTE_ADDR': '1.2.3.4',
        'SERVER_NAME': 'fakehost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': True,
        'wsgi.multiprocess': True
    }
    environ = self.module.build_request_environ('PUT', '/foo?bar=baz',
                                                [('Header', 'Value'),
                                                 ('Other', 'Values')],
                                                six.b('body'), '1.2.3.4', 80)
    self.assertEqual('', environ.pop('wsgi.errors').getvalue())
    self.assertEqual(six.b('body'), environ.pop('wsgi.input').getvalue())
    self.assertEqual(expected_environ, environ)


class TestModuleCreateUrlHandlers(stub_testing.StubTestCase):
  """Tests for module.Module._create_url_handlers."""

  def setUp(self):
    super(TestModuleCreateUrlHandlers, self).setUp()
    self.module_configuration = ModuleConfigurationStub()
    self.instance_factory = InstanceFactoryFacade(None, 1)
    self.servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration)
    # pylint: disable-next=invalid-name
    self.instance_factory.START_URL_MAP = appinfo.URLMap(
        url='/_ah/start', script='start_handler', login='admin')
    # pylint: disable-next=invalid-name
    self.instance_factory.WARMUP_URL_MAP = appinfo.URLMap(
        url='/_ah/warmup', script='warmup_handler', login='admin')
    # Built-in: login, logout, blob_upload, blob_image, gcs, modern default
    self.num_builtin_handlers = 6

  def test_match_all(self):
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'.*', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 1)

  def test_match_start_only(self):
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/_ah/start', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 2)
    self.assertEqual(self.instance_factory.WARMUP_URL_MAP, handlers[0].url_map)

  def test_match_warmup_only(self):
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/_ah/warmup', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 2)
    self.assertEqual(self.instance_factory.START_URL_MAP, handlers[0].url_map)

  def test_match_neither_warmup_nor_start(self):
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 3)
    self.assertEqual(self.instance_factory.WARMUP_URL_MAP, handlers[0].url_map)
    self.assertEqual(self.instance_factory.START_URL_MAP, handlers[1].url_map)

  def test_match_static_only(self):
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/_ah/start', static_dir='foo'),
        appinfo.URLMap(url=r'/_ah/warmup', static_files='foo', upload='foo')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 4)
    self.assertEqual(self.instance_factory.WARMUP_URL_MAP, handlers[0].url_map)
    self.assertEqual(self.instance_factory.START_URL_MAP, handlers[1].url_map)

  def test_match_start_only_no_inbound_warmup(self):
    self.module_configuration.inbound_services = None
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/_ah/start', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 1)

  def test_match_warmup_only_no_inbound_warmup(self):
    self.module_configuration.inbound_services = None
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/_ah/warmup', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 2)
    self.assertEqual(self.instance_factory.START_URL_MAP, handlers[0].url_map)

  def test_match_neither_warmup_nor_start_no_inbound_warmup(self):
    self.module_configuration.inbound_services = None
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    self.assertLen(handlers, self.num_builtin_handlers + 2)
    self.assertEqual(self.instance_factory.START_URL_MAP, handlers[0].url_map)

  def test_endpoints_handler(self):
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/_ah/spi/.*', script=r'foo.py')
    ]
    handlers = self.servr._create_url_handlers()
    # The script handler, /_ah/start, and /_ah/api/.* handler are added.
    self.assertLen(handlers, self.num_builtin_handlers + 3)


class TestModuleGetRuntimeConfig(parameterized.TestCase,
                                 stub_testing.StubTestCase):
  """Tests for module.Module._get_runtime_config."""

  def setUp(self):
    super(TestModuleGetRuntimeConfig, self).setUp()
    self.module_configuration = ModuleConfigurationStub(skip_files='foo')
    self.module_configuration.handlers = [
        appinfo.URLMap(url=r'/static', static_dir='static'),
        appinfo.URLMap(
            url=r'/app_read_static',
            static_dir='app_read_static',
            application_readable=True),
        appinfo.URLMap(
            url=r'/static_images/*.png',
            static_files=r'static_images/\\1',
            upload=r'static_images/*.png'),
        appinfo.URLMap(
            url=r'/app_readable_static_images/*.png',
            static_files=r'app_readable_static_images/\\1',
            upload=r'app_readable_static_images/*.png',
            application_readable=True),
    ]
    self.instance_factory = InstanceFactoryFacade(None, 1)

  def test_static_files_regex(self):
    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration)
    config = servr._get_runtime_config()
    self.assertEqual(
        r'^(static%s.*)|(static_images/*.png)$' % re.escape(os.path.sep),
        config.static_files)

  def test_allow_skipped_files(self):
    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration,
        allow_skipped_files=True)
    config = servr._get_runtime_config()
    self.assertFalse(config.HasField('skip_files'))
    self.assertFalse(config.HasField('static_files'))

  def test_threadsafe_true_override_none(self):
    self.module_configuration.threadsafe = True
    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration)
    config = servr._get_runtime_config()
    self.assertTrue(config.threadsafe)

  def test_threadsafe_false_override_none(self):
    self.module_configuration.threadsafe = False
    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration)
    config = servr._get_runtime_config()
    self.assertFalse(config.threadsafe)

  def test_threadsafe_true_override_false(self):
    self.module_configuration.threadsafe = True
    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration,
        threadsafe_override=False)
    config = servr._get_runtime_config()
    self.assertFalse(config.threadsafe)

  def test_threadsafe_false_override_true(self):
    self.module_configuration.threadsafe = False
    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration,
        threadsafe_override=True)
    config = servr._get_runtime_config()
    self.assertTrue(config.threadsafe)

  @parameterized.parameters(
      ('php82', 'php_config', runtime_config_pb2.PhpConfig),
      ('python312', 'python_config', runtime_config_pb2.PythonConfig),
  )
  def test_copy_runtime_config(self, runtime, field_to_set, field_class):
    module_configuration = ModuleConfigurationStub(runtime=runtime)
    php_config = runtime_config_pb2.PhpConfig()
    python_config = runtime_config_pb2.PhpConfig()

    servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=module_configuration,
        php_config=php_config,
        python_config=python_config,
    )
    config = servr._get_runtime_config()

    self.assertTrue(hasattr(config, field_to_set))
    self.assertEqual(field_class, type(getattr(config, field_to_set)))


class TestModuleShutdownInstance(stub_testing.StubTestCase):
  """Tests for module.Module._shutdown_instance."""

  def setUp(self):
    super(TestModuleShutdownInstance, self).setUp()
    self.mox = mox.Mox()
    self.module_configuration = ModuleConfigurationStub()
    self.instance_factory = NoOpInstanceFactoryFacade(None, 1)
    self.servr = ModuleFacade(
        instance_factory=self.instance_factory,
        module_configuration=self.module_configuration)
    self.mox.StubOutWithMock(logging, 'exception')
    self.mox.StubOutWithMock(self.servr, '_handle_request')
    self.mox.StubOutWithMock(self.servr._quit_event, 'wait')
    self.mox.StubOutWithMock(module.Module, 'build_request_environ')
    self.inst = self.mox.CreateMock(instance.Instance)
    self.time = 0
    self.mox.stubs.Set(time, 'time', lambda: self.time)

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestModuleShutdownInstance, self).tearDown()

  def test_shutdown_instance(self):

    def advance_time(*unused_args, **unused_kwargs):
      self.time += 10

    environ = object()
    self.servr.build_request_environ(
        'GET', '/_ah/stop', [], '', '0.1.0.3', 9000,
        fake_login=True).AndReturn(environ)
    self.servr._handle_request(
        environ,
        start_response_utils.null_start_response,
        inst=self.inst,
        request_type=instance.SHUTDOWN_REQUEST).WithSideEffects(advance_time)
    self.servr._quit_event.wait(20)
    self.inst.quit(force=True)
    self.mox.ReplayAll()
    self.servr._shutdown_instance(self.inst, 9000)
    self.mox.VerifyAll()


class TestModuleRuntime(stub_testing.StubTestCase):
  """Tests for module.Module.runtime."""

  def setUp(self):
    super(TestModuleRuntime, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(application_configuration.ModuleConfiguration,
                             '_parse_configuration')
    self.mox.StubOutWithMock(os.path, 'getmtime')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestModuleRuntime, self).tearDown()

  class ModuleStubRuntime(module.Module):

    def __init__(self, module_configuration):
      self._module_configuration = module_configuration

  def test_vm_false(self):
    automatic_scaling = appinfo.AutomaticScaling(
        min_pending_latency='1.0s',
        max_pending_latency='2.0s',
        min_idle_instances=1,
        max_idle_instances=2)
    error_handlers = [appinfo.ErrorHandlers(file='error.html')]
    handlers = [appinfo.URLMap(url=r'/python-(.*)', script=r'\1.py')]
    info = appinfo.AppInfoExternal(
        application='app',
        module='module1',
        version='1',
        runtime='python312',
        threadsafe=False,
        automatic_scaling=automatic_scaling,
        skip_files=r'\*.gif',
        error_handlers=error_handlers,
        handlers=handlers,
        inbound_services=['warmup'],
        env_variables=appinfo.EnvironmentVariables(),
    )
    config_path = '/appdir/app.yaml'
    application_configuration.ModuleConfiguration._parse_configuration(
        config_path).AndReturn((info, [config_path]))
    os.path.getmtime(config_path).AndReturn(10)

    self.mox.ReplayAll()
    config = application_configuration.ModuleConfiguration('/appdir/app.yaml')
    servr = TestModuleRuntime.ModuleStubRuntime(module_configuration=config)
    self.assertEqual(servr.runtime, 'python312')
    self.assertEqual(servr.effective_runtime, 'python312')
    self.mox.VerifyAll()


class TestAutoScalingModuleWarmup(stub_testing.StubTestCase):
  """Tests for module.AutoScalingModule._warmup."""

  def setUp(self):
    super(TestAutoScalingModuleWarmup, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(module.Module, 'build_request_environ')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingModuleWarmup, self).tearDown()

  def test_warmup(self):
    s = AutoScalingModuleFacade(
        balanced_port=8080,
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.mox.StubOutWithMock(s, '_handle_request')
    self.mox.StubOutWithMock(s._condition, 'notify')

    inst = self.mox.CreateMock(instance.Instance)

    environ = object()
    s.build_request_environ(
        'GET', '/_ah/warmup', [], '', '0.1.0.3', 8080,
        fake_login=True).AndReturn(environ)
    s._handle_request(
        environ,
        mox.IgnoreArg(),
        inst=inst,
        request_type=instance.READY_REQUEST)
    s._condition.notify(1)

    self.mox.ReplayAll()
    s._warmup(inst)
    self.mox.VerifyAll()


class TestAutoScalingModuleAddInstance(stub_testing.StubTestCase):
  """Tests for module.AutoScalingModule._add_instance."""

  def setUp(self):
    super(TestAutoScalingModuleAddInstance, self).setUp()
    self.mox = mox.Mox()
    self.factory = self.mox.CreateMock(instance.InstanceFactory)
    self.factory.max_concurrent_requests = 10

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingModuleAddInstance, self).tearDown()

  def create_server(self, max_instances=None):
    s = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10),
        max_instances=max_instances)
    s._instance_factory = self.factory
    return s

  def test_permit_warmup(self):
    s = self.create_server()
    self.mox.StubOutWithMock(s, '_async_warmup')
    self.mox.StubOutWithMock(s._condition, 'notify')

    inst = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        mox.Regex('[a-f0-9]{36}'), expect_ready_request=True).AndReturn(inst)
    inst.start().AndReturn(True)
    s._async_warmup(inst)

    self.mox.ReplayAll()
    self.assertEqual(inst, s._add_instance(permit_warmup=True))
    self.mox.VerifyAll()

    self.assertLen(s._instances, 1)

  def test_no_permit_warmup(self):
    s = self.create_server()
    self.mox.StubOutWithMock(s._condition, 'notify')

    inst = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        mox.Regex('[a-f0-9]{36}'), expect_ready_request=False).AndReturn(inst)
    inst.start().AndReturn(True)
    s._condition.notify(10)

    self.mox.ReplayAll()
    self.assertEqual(inst, s._add_instance(permit_warmup=False))
    self.mox.VerifyAll()

    self.assertIn(inst, s._instances)

  def test_failed_to_start(self):
    s = self.create_server()
    self.mox.StubOutWithMock(s, '_async_warmup')
    self.mox.StubOutWithMock(s._condition, 'notify')

    inst = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        mox.Regex('[a-f0-9]{36}'), expect_ready_request=True).AndReturn(inst)
    inst.start().AndReturn(False)

    self.mox.ReplayAll()
    self.assertIsNone(s._add_instance(permit_warmup=True))
    self.mox.VerifyAll()

    self.assertLen(s._instances, 1)

  def test_max_instances(self):
    s = self.create_server(max_instances=1)
    self.mox.StubOutWithMock(s._condition, 'notify')

    inst = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        mox.Regex('[a-f0-9]{36}'), expect_ready_request=False).AndReturn(inst)
    inst.start().AndReturn(True)
    s._condition.notify(10)

    self.mox.ReplayAll()
    self.assertEqual(inst, s._add_instance(permit_warmup=False))
    self.assertEqual(None, s._add_instance(permit_warmup=False))
    self.mox.VerifyAll()

    self.assertLen(s._instances, 1)


class TestAutoScalingInstancePoolHandleScriptRequest(stub_testing.StubTestCase
                                                    ):
  """Tests for module.AutoScalingModule.handle."""

  def setUp(self):
    super(TestAutoScalingInstancePoolHandleScriptRequest, self).setUp()
    self.mox = mox.Mox()

    self.inst = self.mox.CreateMock(instance.Instance)
    self.environ = {}
    self.start_response = object()
    self.response = [object()]
    self.url_map = object()
    self.match = object()
    self.request_id = object()
    self.auto_module = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.mox.StubOutWithMock(self.auto_module, '_choose_instance')
    self.mox.StubOutWithMock(self.auto_module, '_add_instance')
    self.mox.stubs.Set(time, 'time', lambda: 0.0)

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolHandleScriptRequest, self).tearDown()

  def test_handle_script_request(self):
    self.auto_module._choose_instance(0.1).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.auto_module._handle_script_request(self.environ,
                                                self.start_response,
                                                self.url_map, self.match,
                                                self.request_id))
    self.mox.VerifyAll()
    self.assertEqual([(mox.IgnoreArg(), 1)],
                     list(self.auto_module._outstanding_request_history))

  def test_handle_cannot_accept_request(self):
    self.auto_module._choose_instance(0.1).AndReturn(self.inst)
    self.auto_module._choose_instance(0.1).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndRaise(
                         instance.CannotAcceptRequests)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.auto_module._handle_script_request(self.environ,
                                                self.start_response,
                                                self.url_map, self.match,
                                                self.request_id))
    self.mox.VerifyAll()
    self.assertEqual([(mox.IgnoreArg(), 1)],
                     list(self.auto_module._outstanding_request_history))

  def test_handle_new_instance(self):
    self.auto_module._choose_instance(0.1).AndReturn(None)
    self.auto_module._add_instance(permit_warmup=False).AndReturn(self.inst)

    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.auto_module._handle_script_request(self.environ,
                                                self.start_response,
                                                self.url_map, self.match,
                                                self.request_id))
    self.mox.VerifyAll()

  def test_handle_new_instance_none_returned(self):
    self.auto_module._choose_instance(0.1).AndReturn(None)
    self.auto_module._add_instance(permit_warmup=False).AndReturn(None)
    self.auto_module._choose_instance(0.2).AndReturn(self.inst)

    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.auto_module._handle_script_request(self.environ,
                                                self.start_response,
                                                self.url_map, self.match,
                                                self.request_id))
    self.mox.VerifyAll()


class TestAutoScalingInstancePoolTrimRequestTimesAndOutstanding(
    stub_testing.StubTestCase):
  """Tests for AutoScalingModule._trim_outstanding_request_history."""

  def test_trim_outstanding_request_history(self):
    servr = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    servr._outstanding_request_history.append((0, 100))
    servr._outstanding_request_history.append((1.0, 101))
    servr._outstanding_request_history.append((1.2, 102))
    servr._outstanding_request_history.append((2.5, 103))

    now = time.time()
    servr._outstanding_request_history.append((now, 42))
    servr._outstanding_request_history.append((now + 1, 43))
    servr._outstanding_request_history.append((now + 3, 44))
    servr._outstanding_request_history.append((now + 4, 45))

    servr._trim_outstanding_request_history()
    self.assertEqual([(now, 42), (now + 1, 43), (now + 3, 44), (now + 4, 45)],
                     list(servr._outstanding_request_history))


class TestAutoScalingInstancePoolGetNumRequiredInstances(
    stub_testing.StubTestCase):
  """Tests for AutoScalingModule._outstanding_request_history."""

  def setUp(self):
    super(TestAutoScalingInstancePoolGetNumRequiredInstances, self).setUp()
    self.servr = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 5))

  def test_get_num_required_instances(self):
    now = time.time()
    self.servr._outstanding_request_history.append((now, 42))
    self.servr._outstanding_request_history.append((now + 1, 43))
    self.servr._outstanding_request_history.append((now + 3, 44))
    self.servr._outstanding_request_history.append((now + 4, 45))
    self.assertEqual(9, self.servr._get_num_required_instances())

  def test_no_requests(self):
    self.assertEqual(0, self.servr._get_num_required_instances())


class TestAutoScalingInstancePoolSplitInstances(stub_testing.StubTestCase):
  """Tests for module.AutoScalingModule._split_instances."""

  class Instance(object):

    def __init__(self, num_outstanding_requests, can_accept_requests=True):
      self.num_outstanding_requests = num_outstanding_requests
      self.can_accept_requests = can_accept_requests

    def __repr__(self):
      return str(self.num_outstanding_requests)

  def setUp(self):
    super(TestAutoScalingInstancePoolSplitInstances, self).setUp()
    self.mox = mox.Mox()
    self.servr = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.mox.StubOutWithMock(self.servr, '_get_num_required_instances')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolSplitInstances, self).tearDown()

  def test_split_instances(self):
    instance1 = self.Instance(1)
    instance2 = self.Instance(2, can_accept_requests=False)
    instance3 = self.Instance(3)
    instance4 = self.Instance(4)
    instance5 = self.Instance(5)
    instance6 = self.Instance(6)
    instance7 = self.Instance(7)
    instance8 = self.Instance(8, can_accept_requests=False)
    instance9 = self.Instance(9)
    instance10 = self.Instance(10)

    self.servr._get_num_required_instances().AndReturn(5)
    self.servr._instances = set([
        instance1, instance2, instance3, instance4, instance5, instance6,
        instance7, instance8, instance9, instance10
    ])

    self.mox.ReplayAll()
    self.assertEqual(
        (set([instance10, instance9, instance7, instance6, instance5
             ]), set([instance1, instance2, instance3, instance4, instance8])),
        self.servr._split_instances())
    self.mox.VerifyAll()

  def test_split_instances_no_instances(self):
    self.servr._get_num_required_instances().AndReturn(5)
    self.servr._instances = set([])

    self.mox.ReplayAll()
    self.assertEqual((set([]), set([])), self.servr._split_instances())
    self.mox.VerifyAll()

  def test_split_instances_no_instances_not_enough_accepting_requests(self):
    instance1 = self.Instance(1)
    instance2 = self.Instance(1, can_accept_requests=False)
    instance3 = self.Instance(2, can_accept_requests=False)

    self.servr._get_num_required_instances().AndReturn(5)
    self.servr._instances = set([instance1, instance2, instance3])

    self.mox.ReplayAll()
    self.assertEqual((set([instance1]), set([instance2, instance3])),
                     self.servr._split_instances())
    self.mox.VerifyAll()

  def test_split_instances_no_required_instances(self):
    instance1 = self.Instance(1)
    instance2 = self.Instance(2, can_accept_requests=False)
    instance3 = self.Instance(3, can_accept_requests=False)
    instance4 = self.Instance(4)
    instance5 = self.Instance(5)
    instance6 = self.Instance(6)
    instance7 = self.Instance(7)
    instance8 = self.Instance(8)

    self.servr._get_num_required_instances().AndReturn(0)
    self.servr._instances = set([
        instance1, instance2, instance3, instance4, instance5, instance6,
        instance7, instance8
    ])

    self.mox.ReplayAll()
    self.assertEqual((set(),
                      set([
                          instance8, instance7, instance6, instance5, instance4,
                          instance3, instance2, instance1
                      ])), self.servr._split_instances())
    self.mox.VerifyAll()


class TestAutoScalingInstancePoolChooseInstances(stub_testing.StubTestCase):
  """Tests for module.AutoScalingModule._choose_instance."""

  class Instance(object):

    def __init__(self, num_outstanding_requests, can_accept_requests=True):
      self.num_outstanding_requests = num_outstanding_requests
      self.remaining_request_capacity = 10 - num_outstanding_requests
      self.can_accept_requests = can_accept_requests

  def setUp(self):
    super(TestAutoScalingInstancePoolChooseInstances, self).setUp()
    self.mox = mox.Mox()
    self.servr = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.mox.StubOutWithMock(self.servr, '_split_instances')
    self.mox.StubOutWithMock(self.servr._condition, 'wait')
    self.time = 10
    self.mox.stubs.Set(time, 'time', lambda: self.time)

  def advance_time(self, *unused_args):
    self.time += 10

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolChooseInstances, self).tearDown()

  def test_choose_instance_required_available(self):
    instance1 = self.Instance(1)
    instance2 = self.Instance(2)
    instance3 = self.Instance(3)
    instance4 = self.Instance(4)

    self.servr._split_instances().AndReturn(
        (set([instance3, instance4]), set([instance1, instance2])))

    self.mox.ReplayAll()
    self.assertEqual(
        instance3,  # Least busy required instance.
        self.servr._choose_instance(15))
    self.mox.VerifyAll()

  def test_choose_instance_no_instances(self):
    self.servr._split_instances().AndReturn((set([]), set([])))
    self.servr._condition.wait(5).WithSideEffects(self.advance_time)

    self.mox.ReplayAll()
    self.assertEqual(None, self.servr._choose_instance(15))
    self.mox.VerifyAll()

  def test_choose_instance_no_instance_that_can_accept_requests(self):
    instance1 = self.Instance(1, can_accept_requests=False)
    self.servr._split_instances().AndReturn((set([]), set([instance1])))
    self.servr._condition.wait(5).WithSideEffects(self.advance_time)

    self.mox.ReplayAll()
    self.assertEqual(None, self.servr._choose_instance(15))
    self.mox.VerifyAll()

  def test_choose_instance_required_full(self):
    instance1 = self.Instance(1)
    instance2 = self.Instance(2)
    instance3 = self.Instance(10)
    instance4 = self.Instance(10)

    self.servr._split_instances().AndReturn(
        (set([instance3, instance4]), set([instance1, instance2])))

    self.mox.ReplayAll()
    self.assertEqual(
        instance2,  # Busyest non-required instance.
        self.servr._choose_instance(15))
    self.mox.VerifyAll()

  def test_choose_instance_must_wait(self):
    instance1 = self.Instance(10)
    instance2 = self.Instance(10)

    self.servr._split_instances().AndReturn(
        (set([instance1]), set([instance2])))
    self.servr._condition.wait(5).WithSideEffects(self.advance_time)

    self.mox.ReplayAll()
    self.assertIsNone(self.servr._choose_instance(15))
    self.mox.VerifyAll()


class TestAutoScalingModuleReportStats(stub_testing.StubTestCase):
  """Test that we report our scaling correctly."""

  def setUp(self):
    super(TestAutoScalingModuleReportStats, self).setUp()
    self.mox = mox.Mox()
    self.servr = AutoScalingModuleFacade(
        module_configuration=ModuleConfigurationStub(
            automatic_scaling=appinfo.AutomaticScaling(
                min_pending_latency='0.1s',
                max_pending_latency='1.0s',
                min_idle_instances=1,
                max_idle_instances=2)),
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.factory = self.mox.CreateMock(instance.InstanceFactory)
    self.factory.max_concurrent_requests = 10
    self.servr._instance_factory = self.factory
    self.mox.StubOutWithMock(self.servr, 'report_quit_metrics')
    self.mox.StubOutWithMock(self.servr, '_split_instances')
    self.mox.StubOutWithMock(self.servr, '_instance_adjustment_thread')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingModuleReportStats, self).tearDown()

  def testShutdownReporting(self):
    """A situation where the number of instances goes up to 2 and then down."""
    inst1 = self.mox.CreateMock(instance.Instance)
    inst2 = self.mox.CreateMock(instance.Instance)
    inst1.num_outstanding_requests = 1
    inst2.num_outstanding_requests = 0

    self.servr._split_instances().AndReturn((set([]), set([])))
    self.factory.new_instance(
        mox.Regex('[a-f0-9]{36}'), expect_ready_request=True).AndReturn(inst1)
    inst1.start()
    self.servr._split_instances().AndReturn((set([inst1]), set([])))
    self.factory.new_instance(
        mox.Regex('[a-f0-9]{36}'), expect_ready_request=True).AndReturn(inst2)
    inst2.start()
    self.servr._split_instances().AndReturn((set([]), set([inst1, inst2])))
    inst1.quit(force=True)
    self.servr._instance_adjustment_thread.join()
    self.servr.report_quit_metrics(2)
    inst2.quit(force=True)
    self.mox.ReplayAll()
    self.servr._adjust_instances()
    self.servr._adjust_instances()
    self.servr._adjust_instances()
    self.servr.quit()
    self.mox.VerifyAll()


class TestAutoScalingInstancePoolAdjustInstances(stub_testing.StubTestCase):
  """Tests for module.AutoScalingModule._adjust_instances."""

  class Instance(object):

    def __init__(self, num_outstanding_requests):
      self.num_outstanding_requests = num_outstanding_requests

    def quit(self):
      pass

  def setUp(self):
    super(TestAutoScalingInstancePoolAdjustInstances, self).setUp()
    self.mox = mox.Mox()
    self.servr = AutoScalingModuleFacade(
        module_configuration=ModuleConfigurationStub(
            automatic_scaling=appinfo.AutomaticScaling(
                min_pending_latency='0.1s',
                max_pending_latency='1.0s',
                min_idle_instances=1,
                max_idle_instances=2)),
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))

    self.mox.StubOutWithMock(self.servr, '_split_instances')
    self.mox.StubOutWithMock(self.servr, '_add_instance')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolAdjustInstances, self).tearDown()

  def test_adjust_instances_create_new(self):
    instance1 = self.Instance(0)
    instance2 = self.Instance(2)
    instance3 = self.Instance(3)
    instance4 = self.Instance(4)

    self.servr._instances = set([instance1, instance2, instance3, instance4])
    self.servr._split_instances().AndReturn(
        (set([instance1, instance2, instance3, instance4]), set([])))
    self.servr._add_instance(permit_warmup=True)

    self.mox.ReplayAll()
    self.servr._adjust_instances()
    self.mox.VerifyAll()

  def test_adjust_instances_quit_idle(self):
    instance1 = self.Instance(0)
    instance2 = self.Instance(2)
    instance3 = self.Instance(3)
    instance4 = self.Instance(4)

    self.mox.StubOutWithMock(instance1, 'quit')

    self.servr._instances = set([instance1, instance2, instance3, instance4])
    self.servr._split_instances().AndReturn(
        (set([]), set([instance1, instance2, instance3, instance4])))
    instance1.quit()

    self.mox.ReplayAll()
    self.servr._adjust_instances()
    self.mox.VerifyAll()

  def test_adjust_instances_quit_idle_with_race(self):
    instance1 = self.Instance(0)
    instance2 = self.Instance(2)
    instance3 = self.Instance(3)
    instance4 = self.Instance(4)

    self.mox.StubOutWithMock(instance1, 'quit')

    self.servr._instances = set([instance1, instance2, instance3, instance4])
    self.servr._split_instances().AndReturn(
        (set([]), set([instance1, instance2, instance3, instance4])))
    instance1.quit().AndRaise(instance.CannotQuitServingInstance)

    self.mox.ReplayAll()
    self.servr._adjust_instances()
    self.mox.VerifyAll()


class InstancePoolHandleChangesBase(stub_testing.StubTestCase):

  def setUp(self):
    super(InstancePoolHandleChangesBase, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(self.instance_factory, 'files_changed')
    self.mox.StubOutWithMock(self.instance_factory, 'configuration_changed')
    self.mox.StubOutWithMock(self.servr, '_create_url_handlers')
    self.mox.StubOutWithMock(self.servr._module_configuration,
                             'check_for_updates')
    self.mox.StubOutWithMock(self.servr._watcher.__class__, 'changes')

    self.metrics_logger = metrics.GetMetricsLogger()
    self.metrics_logger._log_once_on_stop_events = {}

  def tearDown(self):
    self.mox.UnsetStubs()
    super(InstancePoolHandleChangesBase, self).tearDown()

  def _test_file_change_and_report(self):
    """Test detecting file change and reporting them to google analytics."""

    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn({'-'})
    self.instance_factory.files_changed()
    self._restart_module()  # implemented in subclasses
    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.assertEqual(1, self.servr.get_file_change_count())
    result = self.servr.get_watcher_result()
    self.assertIsInstance(result[0], float)
    self.assertEqual(1, result[1])
    self.assertEqual('InotifyFileWatcher', result[2])

    self.mox.VerifyAll()


class TestAutoScalingInstancePoolHandleChanges(InstancePoolHandleChangesBase):
  """Tests for module.AutoScalingModule._handle_changes."""

  def setUp(self):
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    self.servr = AutoScalingModuleFacade(instance_factory=self.instance_factory)
    super(TestAutoScalingInstancePoolHandleChanges, self).setUp()
    self.mox.StubOutWithMock(self.servr, '_maybe_restart_instances')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolHandleChanges, self).tearDown()

  def test_no_changes(self):
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._maybe_restart_instances(
        config_changed=False,
        file_changed=False,
        modern_runtime_dep_libs_changed=None)
    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_irrelevant_config_change(self):
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._maybe_restart_instances(
        config_changed=False,
        file_changed=False,
        modern_runtime_dep_libs_changed=None)

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_restart_config_change(self):
    conf_change = frozenset([application_configuration.ENV_VARIABLES_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.instance_factory.configuration_changed(conf_change)
    self.servr._maybe_restart_instances(
        config_changed=True,
        file_changed=False,
        modern_runtime_dep_libs_changed=None)

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_restart_modern_runtime_dep_libs_changed(self):
    self.instance_factory.dependency_libraries_changed = lambda _: True

    conf_change = frozenset([])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._maybe_restart_instances(
        config_changed=False,
        file_changed=False,
        modern_runtime_dep_libs_changed=True)

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_handler_change(self):
    conf_change = frozenset([application_configuration.HANDLERS_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._create_url_handlers()
    self.instance_factory.configuration_changed(conf_change)
    self.servr._maybe_restart_instances(
        config_changed=True,
        file_changed=False,
        modern_runtime_dep_libs_changed=None)

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def _restart_module(self):
    self.servr._maybe_restart_instances(
        config_changed=False,
        file_changed=True,
        modern_runtime_dep_libs_changed=None)

  def test_file_change_and_report(self):
    self._test_file_change_and_report()


class TestAutoScalingInstancePoolMaybeRestartInstances(
    stub_testing.StubTestCase):
  """Tests for module.AutoScalingModule._maybe_restart_instances."""

  def setUp(self):
    super(TestAutoScalingInstancePoolMaybeRestartInstances, self).setUp()
    self.mox = mox.Mox()
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    # pylint: disable-next=invalid-name
    self.instance_factory.FILE_CHANGE_INSTANCE_RESTART_POLICY = instance.ALWAYS
    self.servr = AutoScalingModuleFacade(instance_factory=self.instance_factory)

    self.inst1 = self.mox.CreateMock(instance.Instance)
    self.inst2 = self.mox.CreateMock(instance.Instance)
    self.inst3 = self.mox.CreateMock(instance.Instance)
    self.inst1.total_requests = 2
    self.inst2.total_requests = 0
    self.inst3.total_requests = 4
    self.servr._instances.add(self.inst1)
    self.servr._instances.add(self.inst2)
    self.servr._instances.add(self.inst3)

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolMaybeRestartInstances, self).tearDown()

  def test_no_changes(self):
    self.mox.ReplayAll()
    self.servr._maybe_restart_instances(
        config_changed=False, file_changed=False)
    self.mox.VerifyAll()

  def test_config_change(self):
    self.inst1.quit(allow_async=True).InAnyOrder()
    self.inst2.quit(allow_async=True).InAnyOrder()
    self.inst3.quit(allow_async=True).InAnyOrder()

    self.mox.ReplayAll()
    self.servr._maybe_restart_instances(config_changed=True, file_changed=False)
    self.mox.VerifyAll()

  def test_file_change_restart_always(self):
    self.instance_factory.FILE_CHANGE_INSTANCE_RESTART_POLICY = instance.ALWAYS
    self.inst1.quit(allow_async=True).InAnyOrder()
    self.inst2.quit(allow_async=True).InAnyOrder()
    self.inst3.quit(allow_async=True).InAnyOrder()

    self.mox.ReplayAll()
    self.servr._maybe_restart_instances(config_changed=False, file_changed=True)
    self.mox.VerifyAll()
    self.assertSequenceEqual(set(), self.servr._instances)

  def test_file_change_restart_after_first_request(self):
    self.instance_factory.FILE_CHANGE_INSTANCE_RESTART_POLICY = (
        instance.AFTER_FIRST_REQUEST)
    self.inst1.quit(allow_async=True).InAnyOrder()
    self.inst3.quit(allow_async=True).InAnyOrder()

    self.mox.ReplayAll()
    self.servr._maybe_restart_instances(config_changed=False, file_changed=True)
    self.mox.VerifyAll()
    self.assertSequenceEqual(set([self.inst2]), self.servr._instances)

  def test_file_change_restart_never(self):
    self.instance_factory.FILE_CHANGE_INSTANCE_RESTART_POLICY = instance.NEVER

    self.mox.ReplayAll()
    self.servr._maybe_restart_instances(config_changed=False, file_changed=True)
    self.mox.VerifyAll()
    self.assertSequenceEqual(
        set([self.inst1, self.inst2, self.inst3]), self.servr._instances)


class TestAutoScalingInstancePoolLoopAdjustingInstances(googletest.TestCase):
  """Tests for module.AutoScalingModule._adjust_instances."""

  def setUp(self):
    super(TestAutoScalingInstancePoolLoopAdjustingInstances, self).setUp()

    self.mox = mox.Mox()
    self.servr = AutoScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestAutoScalingInstancePoolLoopAdjustingInstances, self).tearDown()

  def test_loop_and_quit(self):
    self.mox.StubOutWithMock(self.servr, '_adjust_instances')
    self.mox.StubOutWithMock(self.servr, '_handle_changes')

    inst1 = self.mox.CreateMock(instance.Instance)
    inst2 = self.mox.CreateMock(instance.Instance)
    inst3 = self.mox.CreateMock(instance.Instance)
    self.servr._instances.add(inst1)
    self.servr._instances.add(inst2)
    self.servr._instances.add(inst3)

    self.servr._handle_changes(1000)

    def do_quit(*unused_args):
      self.servr._quit_event.set()

    self.servr._adjust_instances().WithSideEffects(do_quit)

    self.mox.ReplayAll()
    self.servr._loop_adjusting_instances()
    self.mox.VerifyAll()


class TestAutoScalingInstancePoolAutomaticScaling(stub_testing.StubTestCase):

  def _create_module(self, automatic_scaling):
    return AutoScalingModuleFacade(
        module_configuration=ModuleConfigurationStub(
            automatic_scaling=automatic_scaling),
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))

  def test_unset_automatic_settings(self):
    settings = appinfo.AutomaticScaling()
    pool = self._create_module(settings)
    self.assertEqual(0.1, pool._min_pending_latency)
    self.assertEqual(0.5, pool._max_pending_latency)
    self.assertEqual(1, pool._min_idle_instances)
    self.assertEqual(1000, pool._max_idle_instances)

  def test_automatic_automatic_settings(self):
    settings = appinfo.AutomaticScaling(
        min_pending_latency='automatic',
        max_pending_latency='automatic',
        min_idle_instances='automatic',
        max_idle_instances='automatic')
    pool = self._create_module(settings)
    self.assertEqual(0.1, pool._min_pending_latency)
    self.assertEqual(0.5, pool._max_pending_latency)
    self.assertEqual(1, pool._min_idle_instances)
    self.assertEqual(1000, pool._max_idle_instances)

  def test_explicit_automatic_settings(self):
    settings = appinfo.AutomaticScaling(
        min_pending_latency='1234ms',
        max_pending_latency='5.67s',
        min_idle_instances='3',
        max_idle_instances='20')
    pool = self._create_module(settings)
    self.assertEqual(1.234, pool._min_pending_latency)
    self.assertEqual(5.67, pool._max_pending_latency)
    self.assertEqual(3, pool._min_idle_instances)
    self.assertEqual(20, pool._max_idle_instances)


class TestManualScalingModuleStart(stub_testing.StubTestCase):
  """Tests for module.ManualScalingModule._start_instance."""

  def setUp(self):
    super(TestManualScalingModuleStart, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(module.Module, 'build_request_environ')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestManualScalingModuleStart, self).tearDown()

  def create_server(self):
    return ManualScalingModuleFacade(
        balanced_port=8080,
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))

  def test_instance_start_success(self):
    s = self.create_server()
    self.mox.StubOutWithMock(s, '_handle_request')
    self.mox.StubOutWithMock(s._condition, 'notify')

    wsgi_servr = self.mox.CreateMock(wsgi_server.WsgiServer)
    wsgi_servr.port = 12345
    inst = self.mox.CreateMock(instance.Instance)
    inst.instance_id = 0
    inst.start().AndReturn(True)

    environ = object()
    s.build_request_environ(
        'GET', '/_ah/start', [], '', '0.1.0.3', 12345,
        fake_login=True).AndReturn(environ)
    s._handle_request(
        environ,
        mox.IgnoreArg(),
        inst=inst,
        request_type=instance.READY_REQUEST)
    s._condition.notify(1)

    self.mox.ReplayAll()
    s._start_instance(wsgi_servr, inst)
    self.mox.VerifyAll()

  def test_instance_start_failure(self):
    s = self.create_server()
    self.mox.StubOutWithMock(s, '_handle_request')
    self.mox.StubOutWithMock(s._condition, 'notify')

    wsgi_servr = self.mox.CreateMock(wsgi_server.WsgiServer)
    wsgi_servr.port = 12345
    inst = self.mox.CreateMock(instance.Instance)
    inst.instance_id = 0
    inst.start().AndReturn(False)

    self.mox.ReplayAll()
    s._start_instance(wsgi_servr, inst)
    self.mox.VerifyAll()


class TestManualScalingModuleAddInstance(stub_testing.StubTestCase):
  """Tests for module.ManualScalingModule._add_instance."""

  class WsgiServer(object):

    def __init__(self, port):
      self.port = port

  def setUp(self):
    super(TestManualScalingModuleAddInstance, self).setUp()
    self.mox = mox.Mox()
    self.factory = self.mox.CreateMock(instance.InstanceFactory)
    self.factory.max_concurrent_requests = 10

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestManualScalingModuleAddInstance, self).tearDown()

  def create_server(self):
    servr = ManualScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    servr._instance_factory = self.factory
    return servr

  def test_add_while_started(self):
    servr = self.create_server()

    inst = self.mox.CreateMock(instance.Instance)
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    self.mox.StubOutWithMock(wsgi_server.WsgiServer, 'start')
    self.mox.StubOutWithMock(wsgi_server.WsgiServer, 'port')
    wsgi_server.WsgiServer.port = 12345
    self.factory.new_instance(0, expect_ready_request=True).AndReturn(inst)
    wsgi_server.WsgiServer.start()
    module._THREAD_POOL.submit(servr._start_instance,
                               mox.IsA(wsgi_server.WsgiServer), inst)

    self.mox.ReplayAll()
    servr._add_instance()
    self.mox.VerifyAll()
    self.assertIn(inst, servr._instances)
    self.assertEqual((servr, inst), servr._port_registry.get(12345))

  def test_add_while_stopped(self):
    servr = self.create_server()
    servr._suspended = True

    inst = self.mox.CreateMock(instance.Instance)
    self.mox.StubOutWithMock(wsgi_server.WsgiServer, 'start')
    self.mox.StubOutWithMock(wsgi_server.WsgiServer, 'port')
    wsgi_server.WsgiServer.port = 12345
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    self.factory.new_instance(0, expect_ready_request=True).AndReturn(inst)
    wsgi_server.WsgiServer.start()

    self.mox.ReplayAll()
    servr._add_instance()
    self.mox.VerifyAll()

    self.assertIn(inst, servr._instances)
    self.assertEqual((servr, inst), servr._port_registry.get(12345))

  def test_restart_instance(self):
    servr = self.create_server()
    inst = self.mox.CreateMock(instance.Instance)
    new_inst = self.mox.CreateMock(instance.Instance)
    inst.instance_id = 0
    new_inst.instance_id = 0

    self.mox.StubOutWithMock(inst, 'quit')
    self.mox.StubOutWithMock(new_inst, 'start')
    self.mox.StubOutWithMock(self.factory, 'new_instance')

    servr.module_configuration.runtime = 'vm'
    wsgi_servr = self.mox.CreateMock(wsgi_server.WsgiServer)
    self.mox.StubOutWithMock(wsgi_servr, 'set_app')
    wsgi_servr.port = 3
    servr._wsgi_servers = [wsgi_servr]
    servr._instances = [inst]

    inst.quit(force=True)
    wsgi_servr.set_app(mox.IsA(functools.partial))
    self.factory.new_instance(0).AndReturn(new_inst)
    new_inst.start()

    self.mox.ReplayAll()
    servr._restart_instance(inst)
    self.mox.VerifyAll()


class TestManualScalingInstancePoolHandleScriptRequest(
    stub_testing.StubTestCase):
  """Tests for module.ManualScalingModule.handle."""

  def setUp(self):
    super(TestManualScalingInstancePoolHandleScriptRequest, self).setUp()
    self.mox = mox.Mox()

    self.inst = self.mox.CreateMock(instance.Instance)
    self.inst.instance_id = 0
    self.environ = {}
    self.start_response = object()
    self.response = [object()]
    self.url_map = object()
    self.match = object()
    self.request_id = object()
    self.manual_module = ManualScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.mox.StubOutWithMock(self.manual_module, '_choose_instance')
    self.mox.StubOutWithMock(self.manual_module, '_add_instance')
    self.mox.StubOutWithMock(self.manual_module._condition, 'notify')
    self.mox.stubs.Set(time, 'time', lambda: 0.0)

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestManualScalingInstancePoolHandleScriptRequest, self).tearDown()

  def test_handle_script_request(self):
    self.manual_module._choose_instance(10.0).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.manual_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.manual_module._handle_script_request(self.environ,
                                                  self.start_response,
                                                  self.url_map, self.match,
                                                  self.request_id))
    self.mox.VerifyAll()

  def test_handle_cannot_accept_request(self):
    self.manual_module._choose_instance(10.0).AndReturn(self.inst)
    self.manual_module._choose_instance(10.0).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndRaise(
                         instance.CannotAcceptRequests)
    self.manual_module._condition.notify()
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.manual_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.manual_module._handle_script_request(self.environ,
                                                  self.start_response,
                                                  self.url_map, self.match,
                                                  self.request_id))
    self.mox.VerifyAll()

  def test_handle_must_wait(self):
    self.manual_module._choose_instance(10.0).AndReturn(None)
    self.manual_module._choose_instance(10.0).AndReturn(self.inst)

    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.manual_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.manual_module._handle_script_request(self.environ,
                                                  self.start_response,
                                                  self.url_map, self.match,
                                                  self.request_id))
    self.mox.VerifyAll()

  def test_handle_timeout(self):
    self.time = 0.0

    def advance_time(*unused_args):
      self.time += 11

    self.mox.stubs.Set(time, 'time', lambda: self.time)
    self.mox.StubOutWithMock(self.manual_module, '_error_response')

    self.manual_module._choose_instance(10.0).WithSideEffects(advance_time)
    self.manual_module._error_response(self.environ, self.start_response, 503,
                                       mox.IgnoreArg()).AndReturn(self.response)
    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.manual_module._handle_script_request(self.environ,
                                                  self.start_response,
                                                  self.url_map, self.match,
                                                  self.request_id))
    self.mox.VerifyAll()


class TestManualScalingInstancePoolChooseInstances(stub_testing.StubTestCase):
  """Tests for module.ManualScalingModule._choose_instance."""

  class Instance(object):

    def __init__(self, can_accept_requests):
      self.can_accept_requests = can_accept_requests

  def setUp(self):
    self.mox = mox.Mox()
    super(TestManualScalingInstancePoolChooseInstances, self).setUp()
    self.servr = ManualScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.mox.StubOutWithMock(self.servr._condition, 'wait')
    self.time = 0
    self.mox.stubs.Set(time, 'time', lambda: self.time)

  def advance_time(self, *unused_args):
    self.time += 10

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestManualScalingInstancePoolChooseInstances, self).tearDown()

  def test_choose_instance_first_can_accept(self):
    instance1 = self.Instance(True)
    instance2 = self.Instance(True)
    self.servr._instances = [instance1, instance2]
    self.mox.ReplayAll()
    self.assertEqual(instance1, self.servr._choose_instance(1))
    self.mox.VerifyAll()

  def test_choose_instance_first_cannot_accept(self):
    instance1 = self.Instance(False)
    instance2 = self.Instance(True)
    self.servr._instances = [instance1, instance2]
    self.mox.ReplayAll()
    self.assertEqual(instance2, self.servr._choose_instance(1))
    self.mox.VerifyAll()

  def test_choose_instance_none_can_accept(self):
    instance1 = self.Instance(False)
    instance2 = self.Instance(False)
    self.servr._instances = [instance1, instance2]
    self.servr._condition.wait(5).WithSideEffects(self.advance_time)
    self.mox.ReplayAll()
    self.assertEqual(None, self.servr._choose_instance(5))
    self.mox.VerifyAll()

  def test_choose_instance_no_instances(self):
    self.servr._condition.wait(5).WithSideEffects(self.advance_time)
    self.mox.ReplayAll()
    self.assertEqual(None, self.servr._choose_instance(5))
    self.mox.VerifyAll()


class TestManualScalingInstancePoolSetNumInstances(stub_testing.StubTestCase):
  """Tests for module.ManualScalingModule.set_num_instances."""

  def setUp(self):
    super(TestManualScalingInstancePoolSetNumInstances, self).setUp()
    self.mox = mox.Mox()
    self.module = ManualScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self._instance = self.mox.CreateMock(instance.Instance)
    self._wsgi_server = self.mox.CreateMock(wsgi_server.WsgiServer)
    self._wsgi_server.port = 8080
    self.module._instances = [self._instance]
    self.module._wsgi_servers = [self._wsgi_server]
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    self.mox.StubOutWithMock(self.module, '_add_instance')
    self.mox.StubOutWithMock(self.module, '_shutdown_instance')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestManualScalingInstancePoolSetNumInstances, self).tearDown()

  def test_no_op(self):
    self.mox.ReplayAll()
    self.assertEqual(1, self.module.get_num_instances())
    self.module.set_num_instances(1)
    self.mox.VerifyAll()

  def test_add_an_instance(self):
    self.module._add_instance()
    self.mox.ReplayAll()
    self.assertEqual(1, self.module.get_num_instances())
    self.module.set_num_instances(2)
    self.mox.VerifyAll()

  def test_remove_an_instance(self):
    module._THREAD_POOL.submit(self.module._quit_instance, self._instance,
                               self._wsgi_server)
    self._instance.quit(expect_shutdown=True)
    self._wsgi_server.quit()
    self.module._shutdown_instance(self._instance, 8080)
    self.mox.ReplayAll()
    self.assertEqual(1, self.module.get_num_instances())
    self.module.set_num_instances(0)
    self.module._quit_instance(self._instance, self._wsgi_server)
    self.mox.VerifyAll()


class TestManualScalingInstancePoolSuspendAndResume(googletest.TestCase):
  """Tests for module.ManualScalingModule.suspend and resume."""

  def setUp(self):
    super(TestManualScalingInstancePoolSuspendAndResume, self).setUp()
    self.mox = mox.Mox()
    self.module = ManualScalingModuleFacade(
        instance_factory=NoOpInstanceFactoryFacade(object(), 10))
    self.factory = self.mox.CreateMock(instance.InstanceFactory)
    self.module._instance_factory = self.factory
    self._instance = self.mox.CreateMock(instance.Instance)
    self._wsgi_server = wsgi_server.WsgiServer(('localhost', 0), None)
    self.module._instances = [self._instance]
    self.module._wsgi_servers = [self._wsgi_server]
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    self.mox.StubOutWithMock(self.module, '_shutdown_instance')
    self._wsgi_server.start()

  def tearDown(self):
    self._wsgi_server.quit()
    self.mox.UnsetStubs()
    super(TestManualScalingInstancePoolSuspendAndResume, self).tearDown()

  def test_already_suspended(self):
    self.module._suspended = True
    self.assertRaises(request_info.VersionAlreadyStoppedError,
                      self.module.suspend)

  def test_already_resumed(self):
    self.assertRaises(request_info.VersionAlreadyStartedError,
                      self.module.resume)

  def test_suspend_instance(self):
    module._THREAD_POOL.submit(self.module._suspend_instance, self._instance,
                               self._wsgi_server.port)
    self._instance.quit(expect_shutdown=True)
    port = object()
    self.module._shutdown_instance(self._instance, port)
    self.mox.ReplayAll()
    self.module.suspend()
    self.module._suspend_instance(self._instance, port)
    self.mox.VerifyAll()
    self.assertEqual(404, self._wsgi_server._error)
    self.assertEqual(None, self._wsgi_server._app)
    self.assertTrue(self.module._suspended)

  def test_resume(self):
    self.module._suspended = True
    self.module._instances = [object()]
    self.factory.new_instance(
        0, expect_ready_request=True).AndReturn(self._instance)
    module._THREAD_POOL.submit(self.module._start_instance, self._wsgi_server,
                               self._instance)
    self.mox.ReplayAll()
    self.module.resume()
    self.mox.VerifyAll()
    self.assertEqual(self.module._handle_request, self._wsgi_server._app.func)
    self.assertEqual({'inst': self._instance}, self._wsgi_server._app.keywords)
    self.assertFalse(self.module._suspended)

  def test_restart(self):
    self._new_instance = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        0, expect_ready_request=True).AndReturn(self._new_instance)

    f = futures.Future()
    f.set_result(True)
    module._THREAD_POOL.submit(self.module._start_instance, self._wsgi_server,
                               self._new_instance).AndReturn(f)
    self._instance.quit(force=True)
    port = object()
    self.mox.ReplayAll()
    self.module.restart()
    self.mox.VerifyAll()
    self.assertEqual(self.module._handle_request, self._wsgi_server._app.func)
    self.assertEqual({'inst': self._new_instance},
                     self._wsgi_server._app.keywords)
    self.assertFalse(self.module._suspended)


class TestManualScalingInstancePoolHandleChanges(InstancePoolHandleChangesBase):
  """Tests for module.ManualScalingModule._handle_changes."""

  def setUp(self):
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    self.servr = ManualScalingModuleFacade(
        instance_factory=self.instance_factory)
    super(TestManualScalingInstancePoolHandleChanges, self).setUp()
    self.mox.StubOutWithMock(self.servr, 'restart')

  def tearDown(self):
    super(TestManualScalingInstancePoolHandleChanges, self).tearDown()

  def test_no_changes(self):
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn(set())

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_irrelevant_config_change(self):
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn(set())

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_restart_config_change(self):
    conf_change = frozenset([application_configuration.ENV_VARIABLES_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.instance_factory.configuration_changed(conf_change)
    self.servr.restart()

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_handler_change(self):
    conf_change = frozenset([application_configuration.HANDLERS_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._create_url_handlers()
    self.instance_factory.configuration_changed(conf_change)

    self.servr.restart()

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def _restart_module(self):
    self.servr.restart()

  def test_file_change_and_report(self):
    self._test_file_change_and_report()

  def test_restart_config_change_suspended(self):
    self.servr._suspended = True
    conf_change = frozenset([application_configuration.ENV_VARIABLES_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.instance_factory.configuration_changed(conf_change)

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_handler_change_suspended(self):
    self.servr._suspended = True
    conf_change = frozenset([application_configuration.HANDLERS_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._create_url_handlers()
    self.instance_factory.configuration_changed(conf_change)

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_file_change_suspended(self):
    self.servr._suspended = True
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn({'-'})
    self.instance_factory.files_changed()

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()


class TestBasicScalingModuleStart(stub_testing.StubTestCase):
  """Tests for module.BasicScalingModule._start_instance."""

  def setUp(self):
    super(TestBasicScalingModuleStart, self).setUp()
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(module.Module, 'build_request_environ')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestBasicScalingModuleStart, self).tearDown()

  def test_instance_start_success(self):
    s = BasicScalingModuleFacade(
        balanced_port=8080, instance_factory=self.instance_factory)
    self.mox.StubOutWithMock(s, '_handle_request')
    self.mox.StubOutWithMock(s._condition, 'notify')

    wsgi_servr = self.mox.CreateMock(wsgi_server.WsgiServer)
    wsgi_servr.port = 12345
    s._wsgi_servers[0] = wsgi_servr
    inst = self.mox.CreateMock(instance.Instance)
    inst.instance_id = 0
    s._instances[0] = inst
    inst.start().AndReturn(True)

    environ = object()
    s.build_request_environ(
        'GET', '/_ah/start', [], '', '0.1.0.3', 12345,
        fake_login=True).AndReturn(environ)
    s._handle_request(
        environ,
        mox.IgnoreArg(),
        inst=inst,
        request_type=instance.READY_REQUEST)
    s._condition.notify(1)

    self.mox.ReplayAll()
    s._start_instance(0)
    self.mox.VerifyAll()

  def test_instance_start_failure(self):
    s = BasicScalingModuleFacade(
        balanced_port=8080, instance_factory=self.instance_factory)
    self.mox.StubOutWithMock(s, '_handle_request')
    self.mox.StubOutWithMock(s._condition, 'notify')

    wsgi_servr = self.mox.CreateMock(wsgi_server.WsgiServer)
    wsgi_servr.port = 12345
    s._wsgi_servers[0] = wsgi_servr
    inst = self.mox.CreateMock(instance.Instance)
    inst.instance_id = 0
    s._instances[0] = inst
    inst.start().AndReturn(False)

    self.mox.ReplayAll()
    s._start_instance(0)
    self.mox.VerifyAll()

  def test_start_any_instance_success(self):
    s = BasicScalingModuleFacade(
        balanced_port=8080, instance_factory=self.instance_factory)
    s._instance_running = [True, False, False, True]
    inst = object()
    s._instances = [None, inst, None, None]
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    module._THREAD_POOL.submit(s._start_instance, 1)
    self.mox.ReplayAll()
    self.assertEqual(inst, s._start_any_instance())
    self.mox.VerifyAll()
    self.assertEqual([True, True, False, True], s._instance_running)

  def test_start_any_instance_all_already_running(self):
    s = BasicScalingModuleFacade(
        balanced_port=8080, instance_factory=self.instance_factory)
    s._instance_running = [True, True, True, True]
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    self.mox.ReplayAll()
    self.assertIsNone(s._start_any_instance())
    self.mox.VerifyAll()
    self.assertEqual([True, True, True, True], s._instance_running)


class TestBasicScalingInstancePoolHandleScriptRequest(
    stub_testing.StubTestCase):
  """Tests for module.BasicScalingModule.handle."""

  def setUp(self):
    super(TestBasicScalingInstancePoolHandleScriptRequest, self).setUp()
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    self.mox = mox.Mox()
    self.inst = self.mox.CreateMock(instance.Instance)
    self.inst.instance_id = 0
    self.environ = {}
    self.start_response = object()
    self.response = [object()]
    self.url_map = object()
    self.match = object()
    self.request_id = object()
    self.basic_module = BasicScalingModuleFacade(
        instance_factory=self.instance_factory)
    self.mox.StubOutWithMock(self.basic_module, '_choose_instance')
    self.mox.StubOutWithMock(self.basic_module, '_start_any_instance')
    self.mox.StubOutWithMock(self.basic_module, '_start_instance')
    self.mox.StubOutWithMock(self.basic_module._condition, 'wait')
    self.mox.StubOutWithMock(self.basic_module._condition, 'notify')
    self.time = 10
    self.mox.stubs.Set(time, 'time', lambda: self.time)

  def advance_time(self, *unused_args):
    self.time += 11

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestBasicScalingInstancePoolHandleScriptRequest, self).tearDown()

  def test_handle_script_request(self):
    self.basic_module._choose_instance(20).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.basic_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(self.environ,
                                                 self.start_response,
                                                 self.url_map, self.match,
                                                 self.request_id))
    self.mox.VerifyAll()

  def test_handle_cannot_accept_request(self):
    self.basic_module._choose_instance(20).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndRaise(
                         instance.CannotAcceptRequests)
    self.basic_module._condition.notify()
    self.basic_module._choose_instance(20).AndReturn(self.inst)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.basic_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(self.environ,
                                                 self.start_response,
                                                 self.url_map, self.match,
                                                 self.request_id))
    self.mox.VerifyAll()

  def test_handle_timeout(self):
    self.mox.StubOutWithMock(self.basic_module, '_error_response')

    self.basic_module._choose_instance(20).WithSideEffects(self.advance_time)
    self.basic_module._error_response(self.environ, self.start_response, 503,
                                      mox.IgnoreArg()).AndReturn(self.response)

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(self.environ,
                                                 self.start_response,
                                                 self.url_map, self.match,
                                                 self.request_id))
    self.mox.VerifyAll()

  def test_handle_instance(self):
    self.inst.instance_id = 0
    self.inst.has_quit = False

    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.basic_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(
            self.environ,
            self.start_response,
            self.url_map,
            self.match,
            self.request_id,
            inst=self.inst))
    self.mox.VerifyAll()

  def test_handle_instance_start_the_instance(self):
    self.inst.instance_id = 0
    self.inst.has_quit = False

    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndRaise(
                         instance.CannotAcceptRequests)
    self.basic_module._start_instance(0).AndReturn(True)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.basic_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(
            self.environ,
            self.start_response,
            self.url_map,
            self.match,
            self.request_id,
            inst=self.inst))
    self.mox.VerifyAll()

  def test_handle_instance_already_running(self):
    self.inst.instance_id = 0
    self.inst.has_quit = False

    self.basic_module._instance_running[0] = True
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndRaise(
                         instance.CannotAcceptRequests)
    self.inst.wait(20)
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndReturn(self.response)
    self.basic_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(
            self.environ,
            self.start_response,
            self.url_map,
            self.match,
            self.request_id,
            inst=self.inst))
    self.mox.VerifyAll()

  def test_handle_instance_timeout(self):
    self.mox.StubOutWithMock(self.basic_module, '_error_response')

    self.inst.instance_id = 0
    self.inst.has_quit = False

    self.basic_module._instance_running[0] = True
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.NORMAL_REQUEST).AndRaise(
                         instance.CannotAcceptRequests)
    self.inst.wait(20).WithSideEffects(self.advance_time)
    self.basic_module._error_response(self.environ, self.start_response,
                                      503).AndReturn(self.response)
    self.basic_module._condition.notify()

    self.mox.ReplayAll()
    self.assertEqual(
        self.response,
        self.basic_module._handle_script_request(
            self.environ,
            self.start_response,
            self.url_map,
            self.match,
            self.request_id,
            inst=self.inst))
    self.mox.VerifyAll()


class TestBasicScalingInstancePoolChooseInstances(stub_testing.StubTestCase):
  """Tests for module.BasicScalingModule._choose_instance."""

  class Instance(object):

    def __init__(self, can_accept_requests):
      self.can_accept_requests = can_accept_requests

  def setUp(self):
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    super(TestBasicScalingInstancePoolChooseInstances, self).setUp()
    self.mox = mox.Mox()
    self.servr = BasicScalingModuleFacade(
        instance_factory=self.instance_factory)
    self.mox.stubs.Set(time, 'time', lambda: self.time)
    self.mox.StubOutWithMock(self.servr._condition, 'wait')
    self.mox.StubOutWithMock(self.servr, '_start_any_instance')
    self.time = 0

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestBasicScalingInstancePoolChooseInstances, self).tearDown()

  def advance_time(self, *unused_args):
    self.time += 10

  def test_choose_instance_first_can_accept(self):
    instance1 = self.Instance(True)
    instance2 = self.Instance(True)
    self.servr._instances = [instance1, instance2]
    self.mox.ReplayAll()
    self.assertEqual(instance1, self.servr._choose_instance(1))
    self.mox.VerifyAll()

  def test_choose_instance_first_cannot_accept(self):
    instance1 = self.Instance(False)
    instance2 = self.Instance(True)
    self.servr._instances = [instance1, instance2]
    self.mox.ReplayAll()
    self.assertEqual(instance2, self.servr._choose_instance(1))
    self.mox.VerifyAll()

  def test_choose_instance_none_can_accept(self):
    instance1 = self.Instance(False)
    instance2 = self.Instance(False)
    self.servr._instance_running = [True, True]
    self.servr._instances = [instance1, instance2]
    self.servr._start_any_instance().AndReturn(None)
    self.servr._condition.wait(1).WithSideEffects(self.advance_time)
    self.mox.ReplayAll()
    self.assertEqual(None, self.servr._choose_instance(1))
    self.mox.VerifyAll()

  def test_choose_instance_start_an_instance(self):
    instance1 = self.Instance(False)
    instance2 = self.Instance(False)
    mock_instance = self.mox.CreateMock(instance.Instance)
    self.servr._instances = [instance1, instance2]
    self.servr._instance_running = [True, False]
    self.servr._start_any_instance().AndReturn(mock_instance)
    mock_instance.wait(1)
    self.mox.ReplayAll()
    self.assertEqual(mock_instance, self.servr._choose_instance(1))
    self.mox.VerifyAll()

  def test_choose_instance_no_instances(self):
    instance1 = self.Instance(False)
    instance2 = self.Instance(False)
    self.servr._instances = [instance1, instance2]
    self.servr._instance_running = [True, True]
    self.servr._start_any_instance().AndReturn(None)
    self.servr._condition.wait(1).WithSideEffects(self.advance_time)
    self.mox.ReplayAll()
    self.assertEqual(None, self.servr._choose_instance(1))
    self.mox.VerifyAll()


class TestBasicScalingInstancePoolInstanceManagement(stub_testing.StubTestCase
                                                    ):

  def setUp(self):
    super(TestBasicScalingInstancePoolInstanceManagement, self).setUp()
    self.mox = mox.Mox()
    self.factory = self.mox.CreateMock(instance.InstanceFactory)
    self.factory.get_restart_directories = lambda: []
    self.factory.max_concurrent_requests = 10
    self.mox.StubOutWithMock(module._THREAD_POOL, 'submit')
    self.module = BasicScalingModuleFacade(
        # Before replay we construct self.module using a
        # NoOpInstanceFactoryFacade which does not call mocks mocks.
        instance_factory=NoOpInstanceFactoryFacade(
            object(), 10), host='localhost')
    # Now we substitute a mock factory for testing.
    self.module._instance_factory = self.factory
    self.wsgi_server = self.module._wsgi_servers[0]
    self.wsgi_server.start()

  def tearDown(self):
    self.wsgi_server.quit()
    self.mox.UnsetStubs()
    super(TestBasicScalingInstancePoolInstanceManagement, self).tearDown()

  def test_restart(self):
    old_instances = [
        self.mox.CreateMock(instance.Instance),
        self.mox.CreateMock(instance.Instance)
    ]
    self.module._instances = old_instances[:]
    self.module._instance_running = [True, False]
    new_instance = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        0, expect_ready_request=True).AndReturn(new_instance)
    module._THREAD_POOL.submit(self.module._start_instance, 0)
    old_instances[0].quit(expect_shutdown=True)
    module._THREAD_POOL.submit(self.module._shutdown_instance, old_instances[0],
                               self.wsgi_server.port)

    self.mox.ReplayAll()
    self.module.restart()
    self.mox.VerifyAll()
    self.assertEqual([True, False], self.module._instance_running)
    self.assertEqual(new_instance, self.module._instances[0])
    self.assertEqual(self.module._handle_request,
                     self.module._wsgi_servers[0]._app.func)
    self.assertEqual({'inst': new_instance},
                     self.module._wsgi_servers[0]._app.keywords)

  def test_shutdown_idle_instances(self):
    old_instances = [
        self.mox.CreateMock(instance.Instance),
        self.mox.CreateMock(instance.Instance),
        self.mox.CreateMock(instance.Instance)
    ]
    self.module._instances = old_instances[:]
    old_instances[0].idle_seconds = (self.module._instance_idle_timeout + 1)
    old_instances[1].idle_seconds = 0
    old_instances[2].idle_seconds = (self.module._instance_idle_timeout + 1)
    self.module._instance_running = [True, True, False]
    new_instance = self.mox.CreateMock(instance.Instance)
    self.factory.new_instance(
        0, expect_ready_request=True).AndReturn(new_instance)
    old_instances[0].quit(expect_shutdown=True)
    module._THREAD_POOL.submit(self.module._shutdown_instance, old_instances[0],
                               self.wsgi_server.port)

    self.mox.ReplayAll()
    self.module._shutdown_idle_instances()
    self.mox.VerifyAll()
    self.assertEqual([False, True, False], self.module._instance_running)
    self.assertEqual(new_instance, self.module._instances[0])
    self.assertEqual(self.module._handle_request,
                     self.module._wsgi_servers[0]._app.func)
    self.assertEqual({'inst': new_instance},
                     self.module._wsgi_servers[0]._app.keywords)


class TestBasicScalingInstancePoolHandleChanges(InstancePoolHandleChangesBase):
  """Tests for module.BasicScalingModule._handle_changes."""

  def setUp(self):
    self.instance_factory = NoOpInstanceFactoryFacade(object(), 10)
    self.servr = BasicScalingModuleFacade(
        instance_factory=self.instance_factory)
    super(TestBasicScalingInstancePoolHandleChanges, self).setUp()
    self.mox.StubOutWithMock(self.servr, 'restart')

  def test_no_changes(self):
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn(set())

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_irrelevant_config_change(self):
    self.servr._module_configuration.check_for_updates().AndReturn(frozenset())
    self.servr._watcher.changes(0).AndReturn(set())

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_restart_config_change(self):
    conf_change = frozenset([application_configuration.ENV_VARIABLES_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.instance_factory.configuration_changed(conf_change)
    self.servr.restart()

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def test_handler_change(self):
    conf_change = frozenset([application_configuration.HANDLERS_CHANGED])
    self.servr._module_configuration.check_for_updates().AndReturn(conf_change)
    self.servr._watcher.changes(0).AndReturn(set())
    self.servr._create_url_handlers()
    self.instance_factory.configuration_changed(conf_change)
    self.servr.restart()

    self.mox.ReplayAll()
    self.servr._handle_changes()
    self.mox.VerifyAll()

  def _restart_module(self):
    self.servr.restart()

  def test_file_change_and_report(self):
    self._test_file_change_and_report()


class TestExternalModuleGetInstancePort(googletest.TestCase):

  def setUp(self):
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def test_get_instance_port(self):
    s = ExternalModuleFacade(balanced_port=8080)
    s._wsgi_server = self.mox.CreateMock(wsgi_server.WsgiServer)
    s._wsgi_server.port = 8080
    instance_port = s.get_instance_port(0)
    self.assertEqual(8080, instance_port)


class InteractiveCommandModuleFacade(module.InteractiveCommandModule):
  def __init__(self):
    super(InteractiveCommandModuleFacade, self).__init__(
        ModuleConfigurationStub(runtime='python312'),
        'fakehost',
        balanced_port=8000,
        api_host='localhost',
        api_port=9000,
        auth_domain='gmail.com',
        runtime_stderr_loglevel=1,
        php_config=None,
        python_config=None,
        go_config=None,
        custom_config=None,
        cloud_sql_config=None,
        vm_config=None,
        default_version_port=8080,
        port_registry=dispatcher.PortRegistry(),
        request_data=None,
        dispatcher=None,
        use_mtime_file_watcher=False,
        watcher_ignore_re=None,
        allow_skipped_files=False,
        threadsafe_override=None)

  def _create_instance_factory(self, module_configuration):
    return FakeInstanceFactory()


class TestInteractiveCommandModule(stub_testing.StubTestCase):
  def setUp(self):
    super(TestInteractiveCommandModule, self).setUp()

    self.mox = mox.Mox()
    self.inst = self.mox.CreateMock(instance.Instance)
    self.inst.instance_id = 0
    self.environ = object()
    self.start_response = object()
    self.response = [object()]
    self.url_map = object()
    self.match = object()
    self.request_id = object()

    self.servr = InteractiveCommandModuleFacade()
    self.servr._instance_factory.new_instance = self.mox.CreateMockAnything()
    self.mox.StubOutWithMock(self.servr, '_handle_request')
    self.mox.StubOutWithMock(self.servr, 'build_request_environ')

  def test_send_interactive_command(self):

    def good_response(unused_environ, start_response, request_type):
      start_response('200 OK', [])
      return ['10\n']

    environ = object()
    self.servr.build_request_environ('POST', '/', [], 'print 5+5', '192.0.2.0',
                                     8000).AndReturn(environ)
    self.servr._handle_request(
        environ, mox.IgnoreArg(),
        request_type=instance.INTERACTIVE_REQUEST).WithSideEffects(
            good_response)

    self.mox.ReplayAll()
    self.assertEqual(
        six.b('10\n'), self.servr.send_interactive_command('print 5+5'))
    self.mox.VerifyAll()

  def test_send_interactive_command_handle_request_exception(self):
    environ = object()
    self.servr.build_request_environ('POST', '/', [], 'print 5+5', '192.0.2.0',
                                     8000).AndReturn(environ)
    self.servr._handle_request(
        environ, mox.IgnoreArg(),
        request_type=instance.INTERACTIVE_REQUEST).AndRaise(Exception('error'))

    self.mox.ReplayAll()
    self.assertRaisesRegex(errors.InteractiveCommandError, 'error',
                           self.servr.send_interactive_command, 'print 5+5')
    self.mox.VerifyAll()

  def test_send_interactive_command_handle_request_failure(self):

    def good_response(unused_environ, start_response, request_type):
      start_response('503 Service Unavailable', [])
      return ['Instance was restarted while executing command']

    environ = object()
    self.servr.build_request_environ('POST', '/', [], 'print 5+5', '192.0.2.0',
                                     8000).AndReturn(environ)
    self.servr._handle_request(
        environ, mox.IgnoreArg(),
        request_type=instance.INTERACTIVE_REQUEST).WithSideEffects(
            good_response)

    self.mox.ReplayAll()
    self.assertRaisesRegex(errors.InteractiveCommandError,
                           'Instance was restarted while executing command',
                           self.servr.send_interactive_command, 'print 5+5')
    self.mox.VerifyAll()

  def test_handle_script_request(self):
    self.servr._instance_factory.new_instance(
        mox.IgnoreArg(), expect_ready_request=False).AndReturn(self.inst)
    self.inst.start()
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.INTERACTIVE_REQUEST).AndReturn(['10\n'])

    self.mox.ReplayAll()
    self.assertEqual(['10\n'],
                     self.servr._handle_script_request(self.environ,
                                                       self.start_response,
                                                       self.url_map, self.match,
                                                       self.request_id))
    self.mox.VerifyAll()

  def test_handle_script_request_busy(self):
    self.servr._instance_factory.new_instance(
        mox.IgnoreArg(), expect_ready_request=False).AndReturn(self.inst)
    self.inst.start()
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.INTERACTIVE_REQUEST).AndRaise(
                         instance.CannotAcceptRequests())
    self.inst.wait(mox.IgnoreArg())
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.INTERACTIVE_REQUEST).AndReturn(['10\n'])

    self.mox.ReplayAll()
    self.assertEqual(['10\n'],
                     self.servr._handle_script_request(self.environ,
                                                       self.start_response,
                                                       self.url_map, self.match,
                                                       self.request_id))
    self.mox.VerifyAll()

  def test_handle_script_request_timeout(self):
    old_timeout = self.servr._MAX_REQUEST_WAIT_TIME
    try:
      self.servr._MAX_REQUEST_WAIT_TIME = 0  # pylint: disable=invalid-name
      start_response = start_response_utils.CapturingStartResponse()

      self.mox.ReplayAll()
      self.assertEqual(
          ['The command timed-out while waiting for another one to complete'],
          self.servr._handle_script_request(self.environ, start_response,
                                            self.url_map, self.match,
                                            self.request_id))
      self.mox.VerifyAll()
      self.assertEqual('503 Service Unavailable', start_response.status)
    finally:
      # pylint: disable-next=invalid-name
      self.servr._MAX_REQUEST_WAIT_TIME = old_timeout

  def test_handle_script_request_restart(self):

    def restart_and_raise(*args):
      self.servr._inst = None
      raise six.moves.http_client.BadStatusLine('line')

    start_response = start_response_utils.CapturingStartResponse()
    self.servr._instance_factory.new_instance(
        mox.IgnoreArg(), expect_ready_request=False).AndReturn(self.inst)
    self.inst.start()
    self.inst.handle(
        self.environ, start_response, self.url_map, self.match, self.request_id,
        instance.INTERACTIVE_REQUEST).WithSideEffects(restart_and_raise)

    self.mox.ReplayAll()
    self.assertEqual(['Instance was restarted while executing command'],
                     self.servr._handle_script_request(self.environ,
                                                       start_response,
                                                       self.url_map, self.match,
                                                       self.request_id))
    self.mox.VerifyAll()
    self.assertEqual('503 Service Unavailable', start_response.status)

  def test_handle_script_request_unexpected_instance_exception(self):
    self.servr._instance_factory.new_instance(
        mox.IgnoreArg(), expect_ready_request=False).AndReturn(self.inst)
    self.inst.start()
    self.inst.handle(self.environ, self.start_response, self.url_map,
                     self.match, self.request_id,
                     instance.INTERACTIVE_REQUEST).AndRaise(
                         six.moves.http_client.BadStatusLine('line'))

    self.mox.ReplayAll()
    self.assertRaises(six.moves.http_client.BadStatusLine,
                      self.servr._handle_script_request, self.environ,
                      self.start_response, self.url_map, self.match,
                      self.request_id)
    self.mox.VerifyAll()


class InstanceFactoryTest(googletest.TestCase):
  """Tests for the _create_instance_factory method."""

  def setUp(self):
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()
    self.mox.VerifyAll()

  def _run_test(self, runtime, expected_factory_class):
    self.mox.ReplayAll()
    module_configuration = ModuleConfigurationStub(runtime=runtime)
    module_stub = NoHandlersModuleFacade(
        module_configuration=module_configuration)
    instance_factory = module_stub._create_instance_factory(
        module_configuration)
    self.assertIsInstance(instance_factory, expected_factory_class)

  def test_gaego(self):
    self.mox.StubOutWithMock(gaego_application, 'GaeGoApplication')
    gaego_application.GaeGoApplication(mox.IgnoreArg(), mox.IgnoreArg(),
                                       mox.IgnoreArg())
    self._run_test('go122', go_factory.GoRuntimeInstanceFactory)


if __name__ == '__main__':
  googletest.main()
