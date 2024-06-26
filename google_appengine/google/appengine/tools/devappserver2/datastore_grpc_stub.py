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
"""Provides utility functions to create grpc stub and make grpc call."""

import pickle
import threading

import google

from google.appengine.api import apiproxy_stub
from google.appengine.ext.remote_api import remote_api_bytes_pb2
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.runtime import apiproxy_errors
from google.appengine._internal import six


try:
  # pylint: disable=g-import-not-at-top




  import grpc
  from google.appengine.tools.devappserver2 import grpc_service_pb2
except ImportError:
  grpc = None
  grpc_service_pb2 = None

# The timeout in seconds for gRPC calls.
_TIMEOUT = remote_api_stub.TIMEOUT_SECONDS

# The maximum message size for gRPC calls.
_MAX_MESSAGE_LENGTH_BYTES = 1024 * 1024 * 32  # 32MB.


class ConnectionError(Exception):
  """Raised when connection to Cloud Datastore Emulator is lost."""


class DatastoreGrpcStub(apiproxy_stub.APIProxyStub):
  """Wrapper class for CallHandler gRPC service.

  This is a shim between dev appserver and cloud datastore emulator. This
  exposes interfaces common with apiproxy_stub.APIProxyStub (e.g: CreateRPC,
  MakeSyncCall) for maximum backward compatibility.
  """

  def __init__(self, grpc_apiserver_host, txn_add_task_callback_hostport=None):
    """Creates a grpc_service.CallHandler stub.

    Args:
      grpc_apiserver_host: String, the host that CallHandler service listens on.
        Could be in the format of http://hostname:port or hostname:port
      txn_add_task_callback_hostport: String, the host:port for datastore
        emulator to make grpc call to api_server. At the time this code was
        written, the only use case is the callback upon transactional add task
        commit.

    Returns:
      A CallHandler stub.

    Raises:
      RuntimeError: If grpc or grpc_service_pb2 has not been imported.
    """
    super(DatastoreGrpcStub, self).__init__('datastore_v3')
    self.grpc_apiserver_host = self._StripPrefix(grpc_apiserver_host)

    if not grpc:
      raise RuntimeError('The DatastoreGrpcStub requires a local gRPC '
                         'installation, which is not found.')
    if not grpc_service_pb2:
      raise RuntimeError('The DatastoreGrpcStub requires a local gRPC service '
                         'definition, which is not found.')
    self._call_handler_stub_creation_lock = threading.Lock()
    self._call_handler_stub = None
    self._txn_add_task_callback_hostport = self._StripPrefix(
        txn_add_task_callback_hostport)

  def get_or_set_call_handler_stub(self):
    """Get call_handler_stub or instantiate if it has not been created.

    We lazy connect to datastore emulator so that launching api_server does not
    depend on launching datastore emulator.

    Returns:
      A CallHandler stub instance.
    """
    with self._call_handler_stub_creation_lock:
      if not self._call_handler_stub:
        channel = grpc.insecure_channel(
            self.grpc_apiserver_host,
            options=[
                ('grpc.max_receive_message_length', _MAX_MESSAGE_LENGTH_BYTES),
                ('grpc.max_send_message_length', _MAX_MESSAGE_LENGTH_BYTES),
                ('grpc.max_message_length', _MAX_MESSAGE_LENGTH_BYTES)
            ])
        self._call_handler_stub = grpc_service_pb2.CallHandlerStub(channel)
      return self._call_handler_stub

  def Clear(self):
    # api_server.py has _handle_CLEAR() method which requires this interface for
    # reusing api_server between unittests.
    response = six.moves.urllib.request.urlopen(
        six.moves.urllib.request.Request(
            'http://%s/reset' % self.grpc_apiserver_host, data=''.encode()))
    if response.code != six.moves.http_client.OK:
      raise IOError('The Cloud Datastore emulator did not reset successfully.')

  def Write(self):
    # Interface for backward compatibility.
    # api_server.cleanup_stubs() calls this when itself quits.
    # Cloud datastore emulator's life cycle is independent from api server and
    # This method should do nothing.
    pass

  def Flush(self):



    pass

  def SetTxnAddTaskCallbackHostPort(self, txn_add_task_callback_hostport):
    """Set the callback host port.

    Args:
      txn_add_task_callback_hostport: String, the host:port for datastore
        emulator to make grpc call to api_server.
    """
    self._txn_add_task_callback_hostport = self._StripPrefix(
        txn_add_task_callback_hostport)

  def MakeSyncCall(self, service, call, request, response, request_id=None):
    """An interface similar to those exposed by traditional api proxy stubs.

    Args:
      service: Must be 'datastore_v3'.
      call: A string representing the rpc to make. Must be one of the datastore
        v3 methods.
      request: A protocol buffer of the type corresponding to 'call'.
      response: A protocol buffer of the type corresponding to 'call'.
      request_id: A unique string identifying the request associated with the
        API call.

    Raises:
      ConnectionError: connection to the emulator is lost.
    """
    assert service == 'datastore_v3'
    self.CheckRequest(service, call, request)

    request_pb = grpc_service_pb2.Request(  # pytype: disable=module-attr
        service_name=service, method=call, request=request.Encode())
    if call == 'Commit':
      request_pb.txn_add_task_callback_hostport = self._txn_add_task_callback_hostport  # pylint: disable=line-too-long
    if request_id:
      request_pb.request_id = request.request_id()

    try:
      response_pb = self.get_or_set_call_handler_stub().HandleCall(
          request_pb, _TIMEOUT)
    except Exception:  # pylint: disable=broad-except




      raise ConnectionError(
          'Cannot connect to Cloud Datastore Emulator on {}'.format(
              self.grpc_apiserver_host))

    if response_pb.HasField('application_error'):
      app_err = response_pb.application_error
      raise apiproxy_errors.ApplicationError(app_err.code, app_err.detail)

    response.ParseFromString(response_pb.response)

  def MakeSyncCallForRemoteApi(self, request):
    """Translate remote_api_pb.Request to gRPC call.

    Args:
      request: A remote_api_pb.Request message.

    Returns:
      A remote_api_pb.Response message.
    """
    # Translate remote_api_pb.Request into grpc_service_pb2.Request
    return self.MakeSyncCallForRemoteApiPy3(request)

  def MakeSyncCallForRemoteApiPy3(self, request):
    request_pb = grpc_service_pb2.Request(  # pytype: disable=module-attr
        service_name=request.service_name,
        method=request.method,
        request=request.request,
        txn_add_task_callback_hostport=self._txn_add_task_callback_hostport)
    if request.HasField('request_id'):
      request_pb.request_id = request.request_id

    response = remote_api_bytes_pb2.Response()

    try:
      response_pb = self.get_or_set_call_handler_stub().HandleCall(
          request_pb, _TIMEOUT)
    except Exception:  # pylint: disable=broad-except




      response.exception = pickle.dumps(
          # Raising built-in Exception instead of ConnectionError, because the
          # later can not be parsed by remote_api.
          Exception('Cannot connect to Cloud Datastore Emulator on {}'.format(
              self.grpc_apiserver_host)),
          protocol=2)
      return response




    response.response = response_pb.response
    if response_pb.HasField('rpc_error'):
      rpc_error = response_pb.rpc_error
      response_rpc_error = response.rpc_error
      response_rpc_error.code = rpc_error.code
      response_rpc_error.detail = rpc_error.detail
    if response_pb.HasField('application_error'):
      app_err = response_pb.application_error
      response_app_err = response.application_error
      response_app_err.code = app_err.code
      response_app_err.detail = app_err.detail

    return response

  def _StripPrefix(self, host_str):
    prefix = 'http://'
    if not host_str:
      return host_str
    return host_str[len(prefix):] if host_str.startswith(prefix) else host_str
