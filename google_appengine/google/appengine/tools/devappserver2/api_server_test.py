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
"""Tests for google.apphosting.tools.devappserver2.api_server."""

import argparse
import getpass
import itertools
import os
import pickle
import sys
import tempfile
import unittest
from unittest import mock
import urllib
import wsgiref.util

import google

from google.appengine.api import apiproxy_stub
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_service_pb2
from google.appengine.api import user_service_pb2
from google.appengine.api.app_identity import app_identity_stub
from google.appengine.api.capabilities import capability_stub
from google.appengine.api.logservice import logservice_stub
from google.appengine.api.memcache import memcache_stub
from google.appengine.api.taskqueue import taskqueue_stub
from google.appengine.datastore import datastore_pb
from google.appengine.datastore import datastore_sqlite_stub
from google.appengine.datastore import datastore_stub_util
from google.appengine.datastore import datastore_v4_pb2
from google.appengine.ext.remote_api import remote_api_bytes_pb2
from google.appengine.runtime import apiproxy_errors
import mox
from google.appengine._internal import six

from google.appengine.tools.devappserver2 import api_server
from google.appengine.tools.devappserver2 import datastore_grpc_stub
from google.appengine.tools.devappserver2 import metrics
from google.appengine.tools.devappserver2 import shutdown
from google.appengine.tools.devappserver2 import stub_util
from google.appengine.tools.devappserver2 import wsgi_request_info
from google.appengine.tools.devappserver2 import wsgi_test_utils

APP_ID = 'test'
APPLICATION_ROOT = '/tmp'
TRUSTED = False
_, BLOBSTORE_PATH = tempfile.mkstemp(prefix='ae-blobstore')
_, DATASTORE_PATH = tempfile.mkstemp(prefix='ae-datastore')
DATASTORE_REQUIRE_INDEXES = False
IMAGES_HOST_PREFIX = 'localhost:8080'
LOGS_PATH = ':memory:'
MAIL_SMTP_HOST = 'localhost'
MAIL_SMTP_PORT = 80
MAIL_SMTP_USER = 'user'
MAIL_SMTP_PASSWORD = 'abc123'
MAIL_ENABLE_SENDMAIL = False
MAIL_SHOW_MAIL_BODY = True
TASKQUEUE_AUTO_RUN_TASKS = False
TASKQUEUE_DEFAULT_HTTP_SERVER = 'localhost:8080'
USER_LOGIN_URL = 'https://localhost/Login?continue=%s'
USER_LOGOUT_URL = 'https://localhost/Logout?continue=%s'

_DATASTORE_V4_SERVICE_METHOD_NAMES = frozenset(
    datastore_v4_pb2.DESCRIPTOR.services_by_name['DatastoreV4Service']
    .methods_by_name)

request_data = wsgi_request_info.WSGIRequestInfo(None)


class FakeURLFetchServiceStub(apiproxy_stub.APIProxyStub):

  def __init__(self, my_request_data):
    super(FakeURLFetchServiceStub, self).__init__(
        'urlfetch', request_data=my_request_data)

  def _Dynamic_Fetch(self, request, unused_response):
    if request.Url == 'exception':
      raise IOError('the remote error')
    elif request.Url == 'application_error':
      raise apiproxy_errors.ApplicationError(23, 'details')


class FakeDatastoreV4ServiceStub(apiproxy_stub.APIProxyStub):

  def __init__(self, my_request_data=None):
    super(FakeDatastoreV4ServiceStub, self).__init__(
        'datastore_v4', request_data=my_request_data)

  def _Dynamic_BeginTransaction(self, request, response):
    response.transaction = 'whatever'


def setup_stubs():
  """Setup the API stubs. This can only be done once."""
  stub_util.setup_test_stubs(
      request_data,
      app_id=APP_ID,
      application_root=APPLICATION_ROOT,
      trusted=TRUSTED,
      blobstore_path=BLOBSTORE_PATH,
      datastore_consistency=datastore_stub_util.TimeBasedHRConsistencyPolicy(),
      datastore_path=DATASTORE_PATH,
      datastore_require_indexes=DATASTORE_REQUIRE_INDEXES,
      images_host_prefix=IMAGES_HOST_PREFIX,
      logs_path=':memory:',
      mail_smtp_host=MAIL_SMTP_HOST,
      mail_smtp_port=MAIL_SMTP_PORT,
      mail_smtp_user=MAIL_SMTP_USER,
      mail_smtp_password=MAIL_SMTP_PASSWORD,
      mail_enable_sendmail=MAIL_ENABLE_SENDMAIL,
      mail_show_mail_body=MAIL_SHOW_MAIL_BODY,
      taskqueue_auto_run_tasks=TASKQUEUE_AUTO_RUN_TASKS,
      taskqueue_default_http_server=TASKQUEUE_DEFAULT_HTTP_SERVER,
      user_login_url=USER_LOGIN_URL,
      user_logout_url=USER_LOGOUT_URL)
  apiproxy_stub_map.apiproxy.ReplaceStub(
      'urlfetch', FakeURLFetchServiceStub(my_request_data=request_data))
  apiproxy_stub_map.apiproxy.ReplaceStub(
      'datastore_v4', FakeDatastoreV4ServiceStub(my_request_data=request_data))


class APIServerTestBase(wsgi_test_utils.WSGITestCase):
  """Tests for api_server.APIServer."""

  def setUp(self):
    super(APIServerTestBase, self).setUp()
    self.env_patcher = mock.patch.dict(os.environ, {'APPLICATION_ID': APP_ID})
    self.env_patcher.start()
    setup_stubs()
    self.server = api_server.APIServer('localhost', 0, APP_ID)

  def tearDown(self):
    self.env_patcher.stop()
    stub_util.cleanup_stubs()
    super(APIServerTestBase, self).tearDown()

  def _assert_remote_call(self, expected_remote_response, stub_request, service,
                          method):
    """Test a call across the remote API to the API server.

    Args:
      expected_remote_response: the remote response that is expected.
      stub_request: the request protobuf that the stub expects.
      service: the stub's service name.
      method: which service method to call.
    """
    request_environ = {'HTTP_HOST': 'machine:8080'}
    wsgiref.util.setup_testing_defaults(request_environ)

    with request_data.request(request_environ, None) as request_id:
      remote_request = remote_api_bytes_pb2.Request()
      remote_request.service_name = service
      remote_request.method = method
      remote_request.request = stub_request.SerializeToString()
      remote_request.request_id = request_id
      remote_payload = remote_request.SerializeToString()

      environ = {
          'CONTENT_LENGTH': len(remote_payload),
          'REQUEST_METHOD': 'POST',
          'wsgi.input': six.BytesIO(remote_payload)
      }

      expected_headers = {'Content-Type': 'application/octet-stream'}
      self.assertResponse('200 OK', expected_headers,
                          expected_remote_response.SerializeToString(),
                          self.server, environ)


class TestAPIServer(APIServerTestBase):

  def test_user_api_call(self):
    logout_response = user_service_pb2.CreateLogoutURLResponse()
    logout_response.logout_url = (
        USER_LOGOUT_URL %
        six.moves.urllib.parse.quote('http://machine:8080/crazy_logout'))

    expected_remote_response = remote_api_bytes_pb2.Response()
    expected_remote_response.response = logout_response.SerializeToString()

    logout_request = user_service_pb2.CreateLogoutURLRequest()
    logout_request.destination_url = '/crazy_logout'

    self._assert_remote_call(expected_remote_response, logout_request, 'user',
                             'CreateLogoutURL')

  def test_GET(self):
    environ = {'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'rtok=23'}
    self.assertResponse('200 OK', {'Content-Type': 'text/plain'},
                        b"{app_id: test, rtok: '23'}\n", self.server, environ)

  def test_unsupported_method(self):
    environ = {'REQUEST_METHOD': 'HEAD', 'QUERY_STRING': 'rtok=23'}
    self.assertResponse('405 Method Not Allowed', {}, b'', self.server, environ)

  def test_exception(self):
    urlfetch_request = urlfetch_service_pb2.URLFetchRequest()
    urlfetch_request.Url = 'exception'
    urlfetch_request.Method = urlfetch_service_pb2.URLFetchRequest.GET

    expected_remote_response = remote_api_bytes_pb2.Response()
    expected_remote_response.exception = pickle.dumps(
        RuntimeError(repr(IOError('the remote error'))), protocol=2)

    self._assert_remote_call(expected_remote_response, urlfetch_request,
                             'urlfetch', 'Fetch')

  def test_application_error(self):
    urlfetch_request = urlfetch_service_pb2.URLFetchRequest()
    urlfetch_request.Url = 'application_error'
    urlfetch_request.Method = urlfetch_service_pb2.URLFetchRequest.GET

    expected_remote_response = remote_api_bytes_pb2.Response()
    expected_remote_response.application_error.code = 23
    expected_remote_response.application_error.detail = 'details'
    expected_remote_response.exception = pickle.dumps(
        apiproxy_errors.ApplicationError(23, 'details'), protocol=2)

    self._assert_remote_call(expected_remote_response, urlfetch_request,
                             'urlfetch', 'Fetch')


class TestAPIServerWithEmulator(APIServerTestBase):
  """Test ApiServer working with cloud datastore emulator."""

  def setUp(self):
    super(TestAPIServerWithEmulator, self).setUp()
    apiproxy_stub_map.apiproxy.ReplaceStub(
        'datastore_v3', datastore_grpc_stub.DatastoreGrpcStub(''))

  def test_datastore_emulator_request_too_large(self):
    fake_put_request = mock.Mock(
        spec=datastore_pb.PutRequest, wraps=datastore_pb.PutRequest())
    fake_put_request.SerializeToString.side_effect = (
        lambda: six.ensure_binary('x' * (apiproxy_stub.MAX_REQUEST_SIZE + 1)))

    expected_remote_response = remote_api_bytes_pb2.Response()

    expected_remote_response.exception = pickle.dumps(
        apiproxy_errors.RequestTooLargeError(
            six.ensure_text(apiproxy_stub.REQ_SIZE_EXCEEDS_LIMIT_MSG_TEMPLATE %
                            ('datastore_v3', 'Put'))),
        protocol=2)
    self._assert_remote_call(expected_remote_response, fake_put_request,
                             'datastore_v3', 'Put')


class TestApiServerMain(unittest.TestCase):

  @mock.patch.object(api_server, 'create_api_server')
  @mock.patch.object(shutdown, 'wait_until_shutdown')
  @mock.patch.object(metrics._MetricsLogger, 'Start')
  @mock.patch.object(metrics._MetricsLogger, 'Stop')
  @mock.patch.object(
      argparse.ArgumentParser,
      'parse_args',
      return_value=argparse.Namespace(
          google_analytics_client_id='myid',
          google_analytics_user_agent='myagent',
          support_datastore_emulator=True,
          storage_path='/tmp',
          app_id='',
          dev_appserver_log_level='info',
          config_paths=None,
          java_app_base_url=None))
  def testMetrics(self, unused_mock_parse, mock_stop, mock_start,
                  mock_wait_until_shutdown, mock_create_api_server):
    """Tests metrics logging flow is triggered by api_server main()."""
    api_server.main()
    mock_create_api_server.assert_called_once()
    mock_wait_until_shutdown.assert_called_once()
    mock_start.assert_called_once_with(
        'myid',
        user_agent='myagent',
        support_datastore_emulator=True,
        category=metrics.API_SERVER_CATEGORY)
    mock_stop.assert_called_once()


class GetRuntimeOnlyRequestInfo:
  """A request_info that implements get_runtime."""

  def get_runtime(self):
    return 'runtime1'


class WormholeTestRequestInfo:
  """A fake request_info with methods for testing varify_wormhole_usage."""

  KEY_ERROR = 'KeY ErrOr'

  def __init__(self, runtime, app_engine_apis):
    self._runtime = runtime
    self._app_engine_apis = app_engine_apis

  def get_runtime(self, request_id):
    del request_id  # Unused
    if self._runtime == WormholeTestRequestInfo.KEY_ERROR:
      raise KeyError('Expected Key Error')
    return self._runtime

  def get_app_engine_apis(self, request_id):
    del request_id  # Unused
    if self._app_engine_apis == WormholeTestRequestInfo.KEY_ERROR:
      raise KeyError('Expected Key Error')
    return self._app_engine_apis

  def get_module(self, request_id):
    del request_id  # Unused
    return 'module1'


class VerifyWormholeUsageTest(unittest.TestCase):
  """Tests for api_server._verify_wormhole_usage."""

  def setUp(self):
    super(VerifyWormholeUsageTest, self).setUp()
    self._service = 'service1'
    self._method = 'method1'
    self._request_id = 'request_id_1'

  def _create_request(self, request_id=None, service=None):
    remote_request = remote_api_bytes_pb2.Request()
    if service is None:
      service = self._service

    remote_request.service_name = service
    remote_request.method = self._method
    if request_id:
      remote_request.request_id = request_id

    return remote_request

  def _verify_wormhole_usage(self, request_info, request=None):
    """Call api_server._verify_wormhole_usage."""
    if not request:
      request = self._create_request(self._request_id)
    api_server._verify_wormhole_usage(request_info, request)

  def test_request_with_no_request_id_passes(self):
    request_info = object()
    self._verify_wormhole_usage(request_info, self._create_request())

  def test_request_with_no_request_info_passes(self):
    request_info = None
    self._verify_wormhole_usage(request_info)

  def test_request_data_with_no_getruntime_pasess(self):
    request_info = object()
    self._verify_wormhole_usage(request_info)

  def test_request_data_with_no_get_app_engine_apis_pasess(self):
    request_info = GetRuntimeOnlyRequestInfo()
    self._verify_wormhole_usage(request_info,
                                self._create_request(self._request_id))

  def test_request_data_with_get_runtime_key_error_passes(self):
    request_info = WormholeTestRequestInfo(WormholeTestRequestInfo.KEY_ERROR,
                                           True)
    self._verify_wormhole_usage(request_info)

  def test_request_data_with__get_app_engine_apis_key_error__pasess(self):
    request_info = WormholeTestRequestInfo('go114',
                                           WormholeTestRequestInfo.KEY_ERROR)
    self._verify_wormhole_usage(request_info)

  def test_request_for_wormhole_optional_runtime_passes(self):
    request_info = WormholeTestRequestInfo('python27', True)
    self._verify_wormhole_usage(request_info)

  def test_request_missing_needed_app_engine_apis_fails(self):
    request_info = WormholeTestRequestInfo('go114', False)
    self.assertRaises(apiproxy_errors.FeatureNotEnabledError,
                      self._verify_wormhole_usage, request_info)

  def test_wormhole_request_for_unsupported_servce_fails(self):
    request_info = WormholeTestRequestInfo('go114', True)
    # Note In created request, service=service1
    self.assertRaises(apiproxy_errors.CallNotFoundError,
                      self._verify_wormhole_usage, request_info)

  def test_happy_wormhole_request_passes(self):
    request_info = WormholeTestRequestInfo('go114', True)
    service = api_server.WORMHOLE_SERVICES[0]
    self._verify_wormhole_usage(
        request_info, self._create_request(self._request_id, service=service))


class MustEnableWormholeForRuntimeTest(unittest.TestCase):
  """Tests for api_server._must_enable_wormhole_for_runtime."""

  def test_go115_returns_yes(self):
    self.assertTrue(api_server._must_enable_wormhole_for_runtime('go115'))

  def test_go111_returns_no(self):
    self.assertFalse(api_server._must_enable_wormhole_for_runtime('go111'))

  def test_python39_returns_yes(self):
    self.assertTrue(api_server._must_enable_wormhole_for_runtime('python39'))

  def test_python310_returns_yes(self):
    self.assertTrue(api_server._must_enable_wormhole_for_runtime('python310'))

  def test_python27_returns_no(self):
    self.assertFalse(api_server._must_enable_wormhole_for_runtime('python27'))

  def test_php72_returns_yes(self):
    self.assertTrue(api_server._must_enable_wormhole_for_runtime('php72'))

  def test_php55_returns_no(self):
    self.assertFalse(api_server._must_enable_wormhole_for_runtime('php55'))


class GetStoragePathTest(unittest.TestCase):
  """Tests for api_server.get_storage_path."""

  def setUp(self):
    super(GetStoragePathTest, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(api_server, '_generate_storage_paths')

  def tearDown(self):
    super(GetStoragePathTest, self).tearDown()
    self.mox.UnsetStubs()

  def test_no_path_given_directory_does_not_exist(self):
    path = tempfile.mkdtemp()
    os.rmdir(path)
    api_server._generate_storage_paths('example.com_myapp').AndReturn([path])

    self.mox.ReplayAll()
    self.assertEqual(path,
                     api_server.get_storage_path(None, 'dev~example.com:myapp'))
    self.mox.VerifyAll()
    self.assertTrue(os.path.isdir(path))

  def test_no_path_given_directory_exists(self):
    path1 = tempfile.mkdtemp()
    os.chmod(path1, 0o777)
    path2 = tempfile.mkdtemp()  # Made with mode 0700.

    api_server._generate_storage_paths('example.com_myapp').AndReturn(
        [path1, path2])

    self.mox.ReplayAll()
    if sys.platform == 'win32':
      expected_path = path1
    else:
      expected_path = path2
    self.assertEqual(expected_path,
                     api_server.get_storage_path(None, 'dev~example.com:myapp'))
    self.mox.VerifyAll()

  def test_path_given_does_not_exist(self):
    path = tempfile.mkdtemp()
    os.rmdir(path)

    self.assertEqual(path,
                     api_server.get_storage_path(path, 'dev~example.com:myapp'))
    self.assertTrue(os.path.isdir(path))

  def test_path_given_not_directory(self):
    _, path = tempfile.mkstemp()

    self.assertRaises(IOError, api_server.get_storage_path, path,
                      'dev~example.com:myapp')

  def test_path_given_exists(self):
    path = tempfile.mkdtemp()

    self.assertEqual(path,
                     api_server.get_storage_path(path, 'dev~example.com:myapp'))


class GenerateStoragePathsTest(unittest.TestCase):
  """Tests for api_server._generate_storage_paths."""

  def setUp(self):
    super(GenerateStoragePathsTest, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(getpass, 'getuser')
    self.mox.StubOutWithMock(tempfile, 'gettempdir')

  def tearDown(self):
    super(GenerateStoragePathsTest, self).tearDown()
    self.mox.UnsetStubs()

  @unittest.skipUnless(sys.platform.startswith('win'), 'Windows only')
  def test_windows(self):
    tempfile.gettempdir().AndReturn('/tmp')

    self.mox.ReplayAll()
    self.assertEqual([
        os.path.join('/tmp', 'appengine.myapp'),
        os.path.join('/tmp', 'appengine.myapp.1'),
        os.path.join('/tmp', 'appengine.myapp.2')
    ], list(itertools.islice(api_server._generate_storage_paths('myapp'), 3)))
    self.mox.VerifyAll()

  @unittest.skipIf(sys.platform.startswith('win'), 'not on Windows')
  def test_working_getuser(self):
    getpass.getuser().AndReturn('johndoe')
    tempfile.gettempdir().AndReturn('/tmp')

    self.mox.ReplayAll()
    self.assertEqual([
        os.path.join('/tmp', 'appengine.myapp.johndoe'),
        os.path.join('/tmp', 'appengine.myapp.johndoe.1'),
        os.path.join('/tmp', 'appengine.myapp.johndoe.2')
    ], list(itertools.islice(api_server._generate_storage_paths('myapp'), 3)))
    self.mox.VerifyAll()

  @unittest.skipIf(sys.platform.startswith('win'), 'not on Windows')
  def test_broken_getuser(self):
    getpass.getuser().AndRaise(Exception())
    tempfile.gettempdir().AndReturn('/tmp')

    self.mox.ReplayAll()
    self.assertEqual([
        os.path.join('/tmp', 'appengine.myapp'),
        os.path.join('/tmp', 'appengine.myapp.1'),
        os.path.join('/tmp', 'appengine.myapp.2')
    ], list(itertools.islice(api_server._generate_storage_paths('myapp'), 3)))
    self.mox.VerifyAll()


class ClearApiServer(unittest.TestCase):
  """Tests for api_server._handle_CLEAR."""

  def setUp(self):
    super(ClearApiServer, self).setUp()
    self.server = api_server.APIServer('localhost', 0, '')

    self.app_identity_stub = mock.create_autospec(
        app_identity_stub.AppIdentityServiceStub)
    self.capability_stub = mock.create_autospec(
        capability_stub.CapabilityServiceStub)
    self.datastore_v3_stub = mock.create_autospec(
        datastore_sqlite_stub.DatastoreSqliteStub)
    self.logservice_stub = mock.create_autospec(logservice_stub.LogServiceStub)
    self.mail_stub = mock.create_autospec(mail_stub.MailServiceStub)
    self.memcache_stub = mock.create_autospec(memcache_stub.MemcacheServiceStub)
    self.taskqueue_stub = mock.create_autospec(
        taskqueue_stub.TaskQueueServiceStub)
    self.clearable_stubs = set([
        self.app_identity_stub, self.capability_stub, self.datastore_v3_stub,
        self.logservice_stub, self.mail_stub, self.memcache_stub,
        self.taskqueue_stub
    ])

    apiproxy_stub_map.apiproxy.ReplaceStub('app_identity_service',
                                           self.app_identity_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('capability_service',
                                           self.capability_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('datastore_v3',
                                           self.datastore_v3_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('logservice', self.logservice_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('mail', self.mail_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('memcache', self.memcache_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('taskqueue', self.taskqueue_stub)

  def test_clear_all(self):
    """Tests that all stubs are cleared."""
    environ = {'QUERY_STRING': ''}
    self.server._handle_CLEAR(environ, lambda *args: None)
    for stub in self.clearable_stubs:
      getattr(stub, 'Clear').assert_called_once()

  def test_clear_datastore_only(self):
    """Tests that only datastore stub is cleared."""
    environ = {'QUERY_STRING': 'stub=datastore_v3'}
    self.server._handle_CLEAR(environ, lambda *args: None)
    self.datastore_v3_stub.Clear.assert_called_once()
    for stub in self.clearable_stubs - set([self.datastore_v3_stub]):
      getattr(stub, 'Clear').assert_not_called()

  def test_clear_datastore_and_memcache(self):
    """Tests that both datastore and memcache stubs are cleared."""
    environ = {'QUERY_STRING': 'stub=datastore_v3&stub=memcache'}
    self.server._handle_CLEAR(environ, lambda *args: None)
    cleared_stubs = set([self.datastore_v3_stub, self.memcache_stub])
    for stub in cleared_stubs:
      getattr(stub, 'Clear').assert_called_once()
    for stub in self.clearable_stubs - cleared_stubs:
      getattr(stub, 'Clear').assert_not_called()


class LocalJavaAppDispatcherTest(unittest.TestCase):
  """Tests for request_info._LocalJavaAppDispatcher."""

  def setUp(self):
    super(LocalJavaAppDispatcherTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    super(LocalJavaAppDispatcherTest, self).tearDown()
    self.mox.UnsetStubs()

  def testAddRequest(self):
    java_app_base_url = 'http://localhost:8080'
    relative_url = '/_ah/queue'
    body = 'body'
    headers = [('X-Header', 'x-header-value')]

    self.mox.StubOutWithMock(urllib.request, 'urlopen')
    self.mox.StubOutClassWithMocks(urllib.request, 'Request')

    urllib_mock_request = urllib.request.Request(
        url=java_app_base_url + relative_url, data=body, headers=dict(headers))

    urllib_mock_response = self.mox.CreateMock(urllib.request.addinfourl)
    urllib_mock_response.getcode().AndReturn(200)

    urllib.request.urlopen(urllib_mock_request).AndReturn(urllib_mock_response)

    dispatcher = api_server._LocalJavaAppDispatcher(
        java_app_base_url=java_app_base_url)

    self.mox.ReplayAll()
    dispatcher.add_request(
        method='POST',
        relative_url=relative_url,
        headers=headers,
        body=body,
        source_ip='127.0.0.1')
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()
