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


"""An apiproxy stub that calls a remote handler via HTTP.

This allows easy remote access to the App Engine datastore, and potentially any
of the other App Engine APIs, using the same interface you use when accessing
the service locally.

An example Python script:
---
from google.appengine.ext import db
from google.appengine.ext.remote_api import remote_api_stub
from myapp import models
import getpass

def auth_func():
  return (raw_input('Username:'), getpass.getpass('Password:'))

remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func,
                                   'my-app.appspot.com')

# Now you can access the remote datastore just as if your code was running on
# App Engine!

houses = models.House.all().fetch(100)
for a_house in q:
  a_house.doors += 1
db.put(houses)
---

A few caveats:
- Where possible, avoid iterating over queries. Fetching as many results as you
  will need is faster and more efficient. If you don't know how many results
  you need, or you need 'all of them', iterating is fine.
- Likewise, it's a good idea to put entities in batches. Instead of calling put
  for each individual entity, accumulate them and put them in batches using
  db.put(), if you can.
- Requests and responses are still limited to 1MB each, so if you have large
  entities or try and fetch or put many of them at once, your requests may fail.
"""

import datetime
import hashlib
import inspect
import pickle
import random
import sys
import threading

import google

from google import auth as google_auth
from google.appengine.api import api_base_pb2
from google.appengine.api import apiproxy_rpc
from google.appengine.api import apiproxy_stub
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import full_app_id
from google.appengine.api.taskqueue import taskqueue_service_bytes_pb2 as taskqueue_service_pb2
from google.appengine.api.taskqueue import taskqueue_stub
from google.appengine.api.taskqueue import taskqueue_stub_service_bytes_pb2 as taskqueue_stub_service_pb2
from google.appengine.datastore import datastore_pb
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext.remote_api import remote_api_bytes_pb2 as remote_api_pb2
from google.appengine.ext.remote_api import remote_api_services
from google.appengine.runtime import apiproxy_errors
from google.appengine.runtime import context
from google.appengine.runtime.context import ctx_test_util
from google.appengine.tools import google_auth_rpc
from google.auth import jwt
from ruamel import yaml
import six
from six.moves import map
from six.moves import zip
import six.moves._thread
import six.moves.http_cookies

from google.appengine.tools import appengine_rpc






_REQUEST_ID_HEADER = 'HTTP_X_APPENGINE_REQUEST_ID'
_DEVAPPSERVER_LOGIN_COOKIE = 'test@example.com:True:'
TIMEOUT_SECONDS = 10




class Error(Exception):
  """Base class for exceptions in this module."""


class ConfigurationError(Error):
  """Exception for configuration errors."""


class UnknownRemoteServerError(Error):
  """Exception for exceptions returned from a remote_api handler."""


class UnknownJavaServerError(Error):
  """Exception for exceptions returned from a Java remote_api handler."""


def GetUserAgent():
  """Determines the value of the 'User-agent' header to use for HTTP requests.

  Returns:
    String containing the 'user-agent' header value, which includes the SDK
    version, the platform information, and the version of Python;
    e.g., "remote_api/1.0.1 Darwin/9.2.0 Python/2.5.2".
  """
  product_tokens = []

  product_tokens.append("Google-remote_api/1.0")


  product_tokens.append(appengine_rpc.GetPlatformToken())


  python_version = ".".join(str(i) for i in sys.version_info)
  product_tokens.append("Python/%s" % python_version)

  return " ".join(product_tokens)


def GetSourceName():
  return "Google-remote_api-1.0"


def HashEntity(entity):
  """Return a very-likely-unique hash of an entity."""
  return hashlib.sha1(entity.SerializeToString()).digest()


class TransactionData(object):
  """Encapsulates data about an individual transaction."""

  def __init__(self, thread_id, is_xg):


    self.thread_id = thread_id



    self.preconditions = {}




    self.entities = {}

    self.is_xg = is_xg


class RemoteStub(object):
  """A stub for calling services on a remote server over HTTP.

  You can use this to stub out any service that the remote server supports.
  """


  _local = threading.local()

  def __init__(self, server, path, _test_stub_map=None):
    """Constructs a new RemoteStub that communicates with the specified server.

    Args:
      server: An instance of a subclass of
        google.appengine.tools.appengine_rpc.AbstractRpcServer.
      path: The path to the handler this stub should send requests to.
      _test_stub_map: If supplied, send RPC calls to stubs in this map instead
        of over the wire.
    """
    self._server = server
    self._path = path
    self._test_stub_map = _test_stub_map

  def _PreHookHandler(self, service, call, request, response):
    """Executed at the beginning of a MakeSyncCall method call."""
    pass

  def _PostHookHandler(self, service, call, request, response):
    """Executed at the end of a MakeSyncCall method call."""
    pass

  def MakeSyncCall(self, service, call, request, response):
    """The APIProxy entry point for a synchronous API call.

    Args:
      service: A string representing which service to call, e.g: 'datastore_v3'.
      call: A string representing which function to call, e.g: 'put'.
      request: A protocol message for the request, e.g: datastore_pb.PutRequest.
      response: A protocol message for the response, e.g:
        datastore_pb.PutResponse.
    """
    self._PreHookHandler(service, call, request, response)
    try:
      test_stub = self._test_stub_map and self._test_stub_map.GetStub(service)
      if test_stub:

        test_stub.MakeSyncCall(service, call, request, response)
      else:
        self._MakeRealSyncCall(service, call, request, response)
    finally:
      self._PostHookHandler(service, call, request, response)

  @classmethod
  def _GetRequestId(cls):
    """Returns the id of the request associated with the current thread."""
    return cls._local.request_id

  @classmethod
  def _SetRequestId(cls, request_id):
    """Set the id of the request associated with the current thread."""
    cls._local.request_id = request_id

  def _MakeRealSyncCall(self, service, call, request, response):
    """Constructs, sends and receives remote_api.proto."""
    request_pb2 = remote_api_pb2.Request()
    request_pb2.service_name = service
    request_pb2.method = call
    request_pb2.request = request.SerializeToString()
    if hasattr(self._local, 'request_id'):
      request_pb2.request_id = self._local.request_id

    response_pb = remote_api_pb2.Response()
    encoded_request = request_pb2.SerializeToString()
    encoded_response = self._server.Send(self._path, encoded_request)

    response_pb.ParseFromString(encoded_response)

    if response_pb.HasField('application_error'):
      error_pb = response_pb.application_error
      raise apiproxy_errors.ApplicationError(error_pb.code, error_pb.detail)
    elif response_pb.HasField('exception'):

      raise UnknownRemoteServerError('An unknown error has occurred in the '
                                     'remote_api handler for this call: ' +
                                     str(response_pb.exception))
    elif response_pb.HasField('java_exception'):
      raise UnknownJavaServerError('An unknown error has occurred in the '
                                   'Java remote_api handler for this call.')
    else:
      response.ParseFromString(response_pb.response)

  def CreateRPC(self):
    return apiproxy_rpc.RPC(stub=self)


class RemoteDatastoreStub(RemoteStub):
  """A specialised stub for accessing the App Engine datastore remotely.

  A specialised stub is required because there are some datastore operations
  that preserve state between calls. This stub makes queries possible.
  Transactions on the remote datastore are unfortunately still impossible.
  """

  def __init__(self, server, path, default_result_count=20,
               _test_stub_map=None):
    """Constructor.

    Args:
      server: The server name to connect to.
      path: The URI path on the server.
      default_result_count: The number of items to fetch, by default, in a
        datastore Query or Next operation. This affects the batch size of
        query iterators.
    """
    super(RemoteDatastoreStub, self).__init__(server, path, _test_stub_map)
    self.default_result_count = default_result_count
    self.__queries = {}
    self.__transactions = {}




    self.__next_local_cursor = 1
    self.__local_cursor_lock = threading.Lock()
    self.__next_local_tx = 1
    self.__local_tx_lock = threading.Lock()

  def MakeSyncCall(self, service, call, request, response):
    assert service == 'datastore_v3'

    explanation = []
    assert request.IsInitialized(explanation), explanation
    handler = getattr(self, '_Dynamic_' + call, None)
    if handler:
      handler(request, response)
    else:
      super(RemoteDatastoreStub, self).MakeSyncCall(service, call, request,
                                                    response)

    assert response.IsInitialized(explanation), explanation

  def _Dynamic_RunQuery(self, query, query_result, cursor_id = None):
    if query.HasField('transaction'):
      txdata = self.__transactions[query.transaction.handle]
      tx_result = remote_api_pb2.TransactionQueryResult()
      super(RemoteDatastoreStub, self).MakeSyncCall(
          'remote_datastore', 'TransactionQuery', query, tx_result)
      query_result.CopyFrom(tx_result.result)




      eg_key = tx_result.entity_group_key
      encoded_eg_key = eg_key.SerializeToString()
      eg_hash = None
      if tx_result.HasField('entity_group'):
        eg_hash = HashEntity(tx_result.entity_group)
      old_key, old_hash = txdata.preconditions.get(encoded_eg_key, (None, None))
      if old_key is None:
        txdata.preconditions[encoded_eg_key] = (eg_key, eg_hash)
      elif old_hash != eg_hash:
        raise apiproxy_errors.ApplicationError(
            datastore_pb.Error.CONCURRENT_TRANSACTION,
            'Transaction precondition failed.')
    else:
      super(RemoteDatastoreStub, self).MakeSyncCall(
          'datastore_v3', 'RunQuery', query, query_result)

    if cursor_id is None:
      self.__local_cursor_lock.acquire()
      try:
        cursor_id = self.__next_local_cursor
        self.__next_local_cursor += 1
      finally:
        self.__local_cursor_lock.release()

    if query_result.more_results:
      query.offset = query.offset + len(query_result.result)
      if query.HasField('limit'):
        query.limit = query.limit - len(query_result.result)
      self.__queries[cursor_id] = query
    else:
      self.__queries[cursor_id] = None


    query_result.cursor.cursor = cursor_id

  def _Dynamic_Next(self, next_request, query_result):
    assert next_request.offset == 0
    cursor_id = next_request.cursor.cursor
    if cursor_id not in self.__queries:
      raise apiproxy_errors.ApplicationError(datastore_pb.Error.BAD_REQUEST,
                                             'Cursor %d not found' % cursor_id)
    query = self.__queries[cursor_id]

    if query is None:

      query_result.more_results = False
      return
    else:
      if next_request.HasField('count'):
        query.count = next_request.count
      else:
        query.ClearField('count')

    self._Dynamic_RunQuery(query, query_result, cursor_id)




    query_result.skipped_results = 0

  def _Dynamic_Get(self, get_request, get_response):
    txid = None
    if get_request.HasField('transaction'):

      txid = get_request.transaction.handle
      txdata = self.__transactions[txid]
      assert (txdata.thread_id == six.moves._thread.get_ident()
             ), 'Transactions are single-threaded.'


      keys = [(k, k.SerializeToString()) for k in get_request.key]


      new_request = datastore_pb.GetRequest()
      for key, enckey in keys:
        if enckey not in txdata.entities:
          new_request.key.add().CopyFrom(key)
    else:
      new_request = get_request

    if new_request.key:
      super(RemoteDatastoreStub, self).MakeSyncCall(
          'datastore_v3', 'Get', new_request, get_response)

    if txid is not None:

      newkeys = new_request.key
      entities = get_response.entity
      for key, entity in zip(newkeys, entities):
        entity_hash = None
        if entity.HasField('entity'):
          entity_hash = HashEntity(entity.entity)
        txdata.preconditions[key.SerializeToString()] = (key, entity_hash)





      new_response = datastore_pb.GetResponse()
      it = iter(get_response.entity)
      for key, enckey in keys:
        if enckey in txdata.entities:
          cached_entity = txdata.entities[enckey][1]
          if cached_entity:
            new_response.entity.add().entity.CopyFrom(cached_entity)
          else:
            new_response.entity.add()
        else:
          new_entity = next(it)
          if new_entity.HasField('entity'):
            assert new_entity.entity.key == key
            new_response.entity.add().CopyFrom(new_entity)
          else:
            new_response.entity.add()
      get_response.CopyFrom(new_response)

  def _Dynamic_Put(self, put_request, put_response):
    if put_request.HasField('transaction'):
      entities = put_request.entity


      requires_id = lambda x: x.id == 0 and not x.HasField('name')
      new_ents = [e for e in entities if requires_id(e.key.path.element[-1])]
      id_request = datastore_pb.PutRequest()

      txid = put_request.transaction.handle
      txdata = self.__transactions[txid]
      assert (txdata.thread_id == six.moves._thread.get_ident()
             ), 'Transactions are single-threaded.'
      if new_ents:
        for ent in new_ents:
          e = id_request.entity.add()
          e.key.CopyFrom(ent.key)
          e.entity_group.SetInParent()
        id_response = datastore_pb.PutResponse()



        if txdata.is_xg:
          rpc_name = 'GetIDsXG'
        else:
          rpc_name = 'GetIDs'
        super(RemoteDatastoreStub, self).MakeSyncCall(
            'remote_datastore', rpc_name, id_request, id_response)
        assert len(id_request.entity) == len(id_response.key)
        for key, ent in zip(id_response.key, new_ents):
          ent.key.CopyFrom(key)
          ent.entity_group.element.add().CopyFrom(key.path.element[0])

      for entity in entities:
        txdata.entities[entity.key.SerializeToString()] = (entity.key, entity)
        put_response.key.add().CopyFrom(entity.key)
    else:
      super(RemoteDatastoreStub, self).MakeSyncCall(
          'datastore_v3', 'Put', put_request, put_response)

  def _Dynamic_Delete(self, delete_request, response):
    if delete_request.HasField('transaction'):
      txid = delete_request.transaction.handle
      txdata = self.__transactions[txid]
      assert (txdata.thread_id == six.moves._thread.get_ident()
             ), 'Transactions are single-threaded.'
      for key in delete_request.key:
        txdata.entities[key.SerializeToString()] = (key, None)
    else:
      super(RemoteDatastoreStub, self).MakeSyncCall(
          'datastore_v3', 'Delete', delete_request, response)

  def _Dynamic_BeginTransaction(self, request, transaction):
    self.__local_tx_lock.acquire()
    try:
      txid = self.__next_local_tx
      self.__transactions[txid] = TransactionData(six.moves._thread.get_ident(),
                                                  request.allow_multiple_eg)
      self.__next_local_tx += 1
    finally:
      self.__local_tx_lock.release()
    transaction.handle = txid
    transaction.app = request.app

  def _Dynamic_Commit(self, transaction, transaction_response):
    txid = transaction.handle
    if txid not in self.__transactions:
      raise apiproxy_errors.ApplicationError(
          datastore_pb.Error.BAD_REQUEST,
          'Transaction %d not found.' % (txid,))

    txdata = self.__transactions[txid]
    assert (txdata.thread_id == six.moves._thread.get_ident()
           ), 'Transactions are single-threaded.'
    del self.__transactions[txid]

    tx = remote_api_pb2.TransactionRequest()
    tx.allow_multiple_eg = txdata.is_xg
    for key, txhash in txdata.preconditions.values():
      precond = tx.precondition.add()
      precond.key.CopyFrom(key)
      if txhash:
        precond.hash = txhash

    puts = tx.puts
    deletes = tx.deletes
    for key, entity in txdata.entities.values():
      if entity:
        puts.entity.add().CopyFrom(entity)
      else:
        deletes.key.add().CopyFrom(key)


    super(RemoteDatastoreStub, self).MakeSyncCall(
        'remote_datastore', 'Transaction',
        tx, datastore_pb.PutResponse())

  def _Dynamic_Rollback(self, transaction, transaction_response):
    txid = transaction.handle
    self.__local_tx_lock.acquire()
    try:
      if txid not in self.__transactions:
        raise apiproxy_errors.ApplicationError(
            datastore_pb.Error.BAD_REQUEST,
            'Transaction %d not found.' % (txid,))

      txdata = self.__transactions[txid]
      assert (txdata.thread_id == six.moves._thread.get_ident()
             ), 'Transactions are single-threaded.'
      del self.__transactions[txid]
    finally:
      self.__local_tx_lock.release()

  def _Dynamic_CreateIndex(self, index, id_response):
    raise apiproxy_errors.CapabilityDisabledError(
        'The remote datastore does not support index manipulation.')

  def _Dynamic_UpdateIndex(self, index, void):
    raise apiproxy_errors.CapabilityDisabledError(
        'The remote datastore does not support index manipulation.')

  def _Dynamic_DeleteIndex(self, index, void):
    raise apiproxy_errors.CapabilityDisabledError(
        'The remote datastore does not support index manipulation.')


class DatastoreStubTestbedDelegate(RemoteStub):
  """A stub for testbed calling datastore_v3 service in api_server."""

  def __init__(self, server, path,
               max_request_size=apiproxy_stub.MAX_REQUEST_SIZE,
               emulator_port=None):
    super(DatastoreStubTestbedDelegate, self).__init__(server, path)
    self._emulator_port = emulator_port
    self._error_dict = {}
    self._error = None
    self._error_rate = None
    self._max_request_size = max_request_size

  def _PreHookHandler(self, service, call, request, unused_response):
    """Raises an error if request size is too large."""
    if request.ByteSize() > self._max_request_size:
      raise apiproxy_errors.RequestTooLargeError(
          apiproxy_stub.REQ_SIZE_EXCEEDS_LIMIT_MSG_TEMPLATE % (
              service, call))

  def SetConsistencyPolicy(self, consistency_policy):
    """Set the job consistency policy of cloud datastore emulator.

    Args:
      consistency_policy: An instance of
        datastore_stub_util.PseudoRandomHRConsistencyPolicy or
        datastore_stub_util.MasterSlaveConsistencyPolicy.
    """
    datastore_stub_util.UpdateEmulatorConfig(
        port=self._emulator_port, consistency_policy=consistency_policy)
    if isinstance(consistency_policy,
                  datastore_stub_util.PseudoRandomHRConsistencyPolicy):
      consistency_policy.is_using_cloud_datastore_emulator = True
      consistency_policy.emulator_port = self._emulator_port

  def SetAutoIdPolicy(self, auto_id_policy):
    """Set the auto id policy of cloud datastore emulator.

    Args:
      auto_id_policy: A string indicating how the emulator assigns auto IDs,
        should be either datastore_stub_util.SCATTERED or
        datastore_stub_util.SEQUENTIAL.
    """
    datastore_stub_util.UpdateEmulatorConfig(
        port=self._emulator_port, auto_id_policy=auto_id_policy)

  def SetTrusted(self, trusted):
    """A dummy method for backward compatibility unittests.

    Using emulator, the trusted bit is always True.

    Args:
      trusted: boolean. This bit indicates that the app calling the stub is
        trusted. A trusted app can write to datastores of other apps.
    """
    pass

  def __CheckError(self, call):

    exception_type, frequency = self._error_dict.get(call, (None, None))
    if exception_type and frequency:
      if random.random() <= frequency:
        raise exception_type

    if self._error:
      if random.random() <= self._error_rate:
        raise self._error

  def SetError(self, error, method=None, error_rate=1):
    """Set an error condition that may be raised when calls are made to stub.

    If a method is specified, the error will only apply to that call.
    The error rate is applied to the method specified or all calls if
    method is not set.

    Args:
      error: An instance of apiproxy_errors.Error or None for no error.
      method: A string representing the method that the error will affect. e.g:
        'RunQuery'.
      error_rate: a number from [0, 1] that sets the chance of the error,
        defaults to 1.
    """
    if not (error is None or isinstance(error, apiproxy_errors.Error)):
      raise TypeError(
          'error should be None or an instance of apiproxy_errors.Error')
    if method and error:
      self._error_dict[method] = error, error_rate
    else:
      self._error_rate = error_rate
      self._error = error

  def Clear(self):
    """Clears the datastore, deletes all entities and queries."""
    self._server.Send('/clear?service=datastore_v3')

  def MakeSyncCall(self, service, call, request, response):
    self.__CheckError(call)
    super(DatastoreStubTestbedDelegate, self).MakeSyncCall(
        service, call, request, response)


class TaskqueueStubTestbedDelegate(RemoteStub):
  """A stub for testbed calling taskqueue service in api_server.

  Some tests directly call taskqueue_stub methods. When taskqueue service use
  RemoteStub, we need to continue supporting these interfaces.
  """

  def __init__(self, server, path):
    super(TaskqueueStubTestbedDelegate, self).__init__(server, path)
    self.service = 'taskqueue'
    self.get_filtered_tasks = self.GetFilteredTasks
    self._queue_yaml_parser = None

  def SetUpStub(self, **stub_kw_args):
    self._root_path = None
    self._RemoteSetUpStub(**stub_kw_args)

  def GetQueues(self):
    """Delegating TaskQueueServiceStub.GetQueues."""
    request = api_base_pb2.VoidProto()
    response = taskqueue_stub_service_pb2.GetQueuesResponse()
    self.MakeSyncCall('taskqueue', 'GetQueues', request, response)
    return taskqueue_stub.ConvertGetQueuesResponseToQueuesDicts(response)

  def GetTasks(self, queue_name):
    """Delegating TaskQueueServiceStub.GetTasks.

    Args:
      queue_name: String, the name of the queue to return tasks for.

    Returns:
      A list of dictionaries, where each dictionary contains one task's
        attributes.
    """
    request = taskqueue_stub_service_pb2.GetFilteredTasksRequest()
    request.queue_names.append(queue_name)
    response = taskqueue_stub_service_pb2.GetFilteredTasksResponse()
    self.MakeSyncCall('taskqueue', 'GetFilteredTasks', request, response)
    res = []
    for i, eta_delta in enumerate(response.eta_delta):



      task_dict = taskqueue_stub.QueryTasksResponseToDict(
          queue_name, response.query_tasks_response().task(i),


          datetime.datetime.now())
      task_dict['eta_delta'] = eta_delta
      res.append(task_dict)
    return res

  def DeleteTask(self, queue_name, task_name):
    """Delegating TaskQueueServiceStub.DeleteTask.

    Args:
      queue_name: String, the name of the queue to delete the task from.
      task_name: String, the name of the task to delete.
    """
    request = taskqueue_service_pb2.TaskQueueDeleteRequest()
    request.queue_name = queue_name
    request.task_name.append(task_name)
    response = api_base_pb2.VoidProto()
    self.MakeSyncCall('taskqueue', 'DeleteTask', request, response)

  def FlushQueue(self, queue_name):
    """Delegating TaskQueueServiceStub.FlushQueue.

    Args:
      queue_name: String, the name of the queue to flush.
    """
    request = taskqueue_stub_service_pb2.FlushQueueRequest()
    request.queue_name = queue_name
    response = api_base_pb2.VoidProto()
    self.MakeSyncCall('taskqueue', 'FlushQueue', request, response)

  def GetFilteredTasks(self, url='', name='', queue_names=()):
    """Delegating TaskQueueServiceStub.get_filtered_tasks.

    Args:
      url: A string URL that represents the URL all returned tasks point at.
      name: The string name of all returned tasks.
      queue_names: A string queue_name, or a list of string queue names to
        retrieve tasks from. If left blank this will get default to all
        queues available.

    Returns:
      A list of taskqueue.Task objects.
    """
    request = taskqueue_stub_service_pb2.GetFilteredTasksRequest()
    request.url = url
    request.name = name

    if isinstance(queue_names, six.string_types):
      queue_names = [queue_names]
    list(map(request.add_queue_names, queue_names))
    response = taskqueue_stub_service_pb2.GetFilteredTasksResponse()
    self.MakeSyncCall('taskqueue', 'GetFilteredTasks', request, response)

    res = []
    for i, eta_delta in enumerate(response.eta_delta):

      task_dict = taskqueue_stub.QueryTasksResponseToDict(

          '',
          response.query_tasks_response.task[i],
          datetime.datetime.now())
      task_dict['eta_delta'] = eta_delta
      res.append(taskqueue_stub.ConvertTaskDictToTaskObject(task_dict))
    return res

  @property
  def queue_yaml_parser(self):
    """Returns the queue_yaml_parser property."""
    return self._queue_yaml_parser

  @queue_yaml_parser.setter
  def queue_yaml_parser(self, queue_yaml_parser):
    """Sets the queue_yaml_parser as a property."""
    if not callable(queue_yaml_parser):
      raise TypeError(
          'queue_yaml_parser should be callable. Received type: %s' %
          type(queue_yaml_parser))
    request = taskqueue_stub_service_pb2.PatchQueueYamlParserRequest()
    request.patched_return_value = pickle.dumps(
        queue_yaml_parser(self._root_path))
    response = api_base_pb2.VoidProto()
    self._queue_yaml_parser = queue_yaml_parser
    self.MakeSyncCall('taskqueue', 'PatchQueueYamlParser', request, response)

  def _RemoteSetUpStub(self, **kwargs):
    """Set up the stub in api_server with the parameters needed by user test.

    Args:
      **kwargs: Key word arguments that are passed to the service stub
        constructor.
    """
    request = taskqueue_stub_service_pb2.SetUpStubRequest()
    init_args = inspect.getfullargspec(
        taskqueue_stub.TaskQueueServiceStub.__init__)
    for field in set(init_args.args[1:]) - set(['request_data']):
      if field in kwargs:
        setattr(request, field, kwargs[field])
    if 'request_data' in kwargs:
      request.request_data = pickle.dumps(kwargs['request_data'])
    response = api_base_pb2.VoidProto()
    self.MakeSyncCall('taskqueue', 'SetUpStub', request, response)


ALL_SERVICES = set(remote_api_services.SERVICE_PB_MAP)


def GetRemoteAppIdFromServer(server, path, remote_token=None):
  """Return the app id from a connection to an existing server.

  Args:
    server: An appengine_rpc.AbstractRpcServer
    path: The path to the remote_api handler for your app
      (for example, '/_ah/remote_api').
    remote_token: Token to validate that the response was to this request.

  Returns:
    App ID as reported by the remote server.

  Raises:
    ConfigurationError: The server returned an invalid response.
  """
  if not remote_token:
    random.seed()
    remote_token = str(random.random())[2:]
  remote_token = str(remote_token)
  urlargs = {'rtok': remote_token}
  response = server.Send(path, payload=None, **urlargs)
  if not response.startswith(b'{'):
    raise ConfigurationError(
        'Invalid response received from server: %s' % response)
  app_info = yaml.load(response)
  if not app_info or 'rtok' not in app_info or 'app_id' not in app_info:
    raise ConfigurationError('Error parsing app_id lookup response')
  if str(app_info['rtok']) != remote_token:
    raise ConfigurationError('Token validation failed during app_id lookup. '
                             '(sent %s, got %s)' % (repr(remote_token),
                                                    repr(app_info['rtok'])))
  return app_info['app_id']


def ConfigureRemoteApiFromServer(server,
                                 path,
                                 app_id,
                                 services=None,
                                 apiproxy=None,
                                 default_auth_domain=None,
                                 use_remote_datastore=True,
                                 **kwargs):
  """Does necessary setup to allow easy remote access to App Engine APIs.

  Args:
    server: An AbstractRpcServer
    path: The path to the remote_api handler for your app
      (for example, '/_ah/remote_api').
    app_id: The app_id of your app, as declared in app.yaml.
    services: A list of services to set up stubs for. If specified, only those
      services are configured; by default all supported services are configured.
    apiproxy: An apiproxy_stub_map.APIProxyStubMap object. Supplied when there's
      already a apiproxy stub map set up. One example use case is when testbed
      configures remote_api for part of the APIs.
    default_auth_domain: The authentication domain to use by default.
    use_remote_datastore: Whether to use RemoteDatastoreStub instead of passing
      through datastore requests. RemoteDatastoreStub batches transactional
      datastore requests since, in production, datastore requires are scoped to
      a single request.
    **kwargs: Additional kwargs to pass to RemoteStub constructor.
  Raises:
    urllib2.HTTPError: if app_id is not provided and there is an error while
      retrieving it.
    ConfigurationError: if there is a error configuring the Remote API.
  """
  if services is None:
    services = set(ALL_SERVICES)
  else:
    services = set(services)
    unsupported = services.difference(ALL_SERVICES)
    if unsupported:
      raise ConfigurationError('Unsupported service(s): %s'
                               % (', '.join(unsupported),))

  full_app_id.put(app_id)
  if not context.get('AUTH_DOMAIN', None):
    ctx_test_util.set_both('AUTH_DOMAIN', default_auth_domain or 'gmail.com')
  if not apiproxy:
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
  if 'datastore_v3' in services and use_remote_datastore:
    services.remove('datastore_v3')
    datastore_stub = RemoteDatastoreStub(server, path)
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', datastore_stub)
  stub = RemoteStub(server, path, **kwargs)
  for service in services:
    apiproxy_stub_map.apiproxy.RegisterStub(service, stub)


def GetRemoteAppId(servername,
                   path,
                   auth_func,
                   rpc_server_factory=appengine_rpc.HttpRpcServer,
                   rtok=None,
                   secure=False,
                   save_cookies=False):
  """Get the remote appid as reported at servername/path.

  This will also return an AbstractRpcServer server, which can be used with
  ConfigureRemoteApiFromServer.

  Args:
    servername: The hostname your app is deployed on.
    path: The path to the remote_api handler for your app
      (for example, '/_ah/remote_api').
    auth_func: A function that takes no arguments and returns a
      (username, password) tuple. This will be called if your application
      requires authentication to access the remote_api handler (it should!)
      and you do not already have a valid auth cookie.
      <app_id>.appspot.com.
    rpc_server_factory: A factory to construct the rpc server for the datastore.
    rtok: The validation token to sent with app_id lookups. If None, a random
      token is used.
    secure: Use SSL when communicating with the server.
    save_cookies: Forwarded to rpc_server_factory function.

  Returns:
    (app_id, server): The application ID and an AbstractRpcServer.
  """



  server = rpc_server_factory(servername, auth_func, GetUserAgent(),
                              GetSourceName(), save_cookies=save_cookies,
                              debug_data=False, secure=secure,
                              ignore_certs=True)
  app_id = GetRemoteAppIdFromServer(server, path, rtok)
  return app_id, server



_OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/appengine.apis',
    'https://www.googleapis.com/auth/userinfo.email',
    ]


def ConfigureRemoteApiForOAuth(
    servername, path, secure=True, service_account=None, key_file_path=None,
    oauth2_parameters=None, save_cookies=False, auth_tries=3,
    rpc_server_factory=None, app_id=None):
  """Does necessary setup to allow easy remote access to App Engine APIs.

  This function uses OAuth2 with Application Default Credentials
  to communicate with App Engine APIs.

  For more information on Application Default Credentials, see:
  https://developers.google.com/accounts/docs/application-default-credentials

  Args:
    servername: The hostname your app is deployed on.
    path: The path to the remote_api handler for your app
      (for example, '/_ah/remote_api').
    secure: If true, will use SSL to communicate with server. Unlike
      ConfigureRemoteApi, this is true by default.
    service_account: The email address of the service account to use for
      making OAuth requests. If none, the application default will be used
      instead.
    key_file_path: The path to a .p12 file containing the private key for
      service_account. Must be set if service_account is provided.
    oauth2_parameters: None, or an
      appengine_rpc_httplib2.HttpRpcServerOAuth2.OAuth2Parameters object
      representing the OAuth2 parameters for this connection.
    save_cookies: If true, save OAuth2 information in a file.
    auth_tries: Number of attempts to make to authenticate.
    rpc_server_factory: Factory to make RPC server instances.
    app_id: The app_id of your app, as declared in app.yaml, or None.

  Returns:
    server, a server which may be useful for calling the application directly.

  Raises:
    urllib2.HTTPError: if there is an error while retrieving the app id.
    ConfigurationError: if there is a error configuring the DatstoreFileStub.
    ImportError: if the oauth2client or appengine_rpc_httplib2
      module is not available.
    ValueError: if only one of service_account and key_file_path is provided.
  """

  if bool(service_account) != bool(key_file_path):
    raise ValueError('Must provide both service_account and key_file_path.')

  rpc_server_factory = (
      rpc_server_factory or google_auth_rpc.GoogleAuthRpcServer)

  if not oauth2_parameters:
    if key_file_path:
      credentials = jwt.Credentials.from_service_account_file(key_file_path)
    else:
      credentials, _ = google_auth.default(_OAUTH_SCOPES)


    oauth2_parameters = (
        google_auth_rpc.GoogleAuthRpcServer.OAuth2Parameters(
            access_token=None,
            client_id=None,
            client_secret=None,
            scope=_OAUTH_SCOPES,
            refresh_token=None,
            credential_file=None,
            credentials=credentials))

  return ConfigureRemoteApi(
      app_id=app_id,
      path=path,
      auth_func=oauth2_parameters,
      servername=servername,
      secure=secure,
      save_cookies=save_cookies,
      auth_tries=auth_tries,
      rpc_server_factory=rpc_server_factory)


def ConfigureRemoteApi(app_id,
                       path,
                       auth_func,
                       servername=None,
                       rpc_server_factory=appengine_rpc.HttpRpcServer,
                       rtok=None,
                       secure=False,
                       services=None,
                       apiproxy=None,
                       default_auth_domain=None,
                       save_cookies=False,
                       auth_tries=3,
                       use_remote_datastore=True,
                       **kwargs):
  """Does necessary setup to allow easy remote access to App Engine APIs.

  Either servername must be provided or app_id must not be None.  If app_id
  is None and a servername is provided, this function will send a request
  to the server to retrieve the app_id.

  Note that if the app_id is specified, the internal appid must be used;
  this may include a partition and a domain. It is often easier to let
  remote_api_stub retrieve the app_id automatically.

  Args:
    app_id: The app_id of your app, as declared in app.yaml, or None.
    path: The path to the remote_api handler for your app
      (for example, '/_ah/remote_api').
    auth_func: If rpc_server_factory=appengine_rpc.HttpRpcServer, auth_func is
      a function that takes no arguments and returns a
      (username, password) tuple. This will be called if your application
      requires authentication to access the remote_api handler (it should!)
      and you do not already have a valid auth cookie.
      If rpc_server_factory=appengine_rpc_httplib2.HttpRpcServerOAuth2,
      auth_func is appengine_rpc_httplib2.HttpRpcServerOAuth2.OAuth2Parameters.
    servername: The hostname your app is deployed on. Defaults to
      <app_id>.appspot.com.
    rpc_server_factory: A factory to construct the rpc server for the datastore.
    rtok: The validation token to sent with app_id lookups. If None, a random
      token is used.
    secure: Use SSL when communicating with the server.
    services: A list of services to set up stubs for. If specified, only those
      services are configured; by default all supported services are configured.
    apiproxy: An apiproxy_stub_map.APIProxyStubMap object. Supplied when there's
      already a apiproxy stub map set up. One example use case is when testbed
      configures remote_api for part of the APIs.
    default_auth_domain: The authentication domain to use by default.
    save_cookies: Forwarded to rpc_server_factory function.
    auth_tries: Number of attempts to make to authenticate.
    use_remote_datastore: Whether to use RemoteDatastoreStub instead of passing
      through datastore requests. RemoteDatastoreStub batches transactional
      datastore requests since, in production, datastore requires are scoped to
      a single request.
    **kwargs: Additional kwargs to pass to ConfigureRemoteApiFromServer.
  Returns:
    server, the server created by rpc_server_factory, which may be useful for
      calling the application directly.

  Raises:
    urllib2.HTTPError: if app_id is not provided and there is an error while
      retrieving it.
    ConfigurationError: if there is a error configuring the DatstoreFileStub.
  """
  if not servername and not app_id:
    raise ConfigurationError('app_id or servername required')
  if not servername:
    servername = '%s.appspot.com' % (app_id,)
  extra_headers = {}
  if servername.startswith('localhost'):





    cookie = six.moves.http_cookies.SimpleCookie()
    cookie['dev_appserver_login'] = _DEVAPPSERVER_LOGIN_COOKIE
    extra_headers['COOKIE'] = cookie['dev_appserver_login'].OutputString()



  server = rpc_server_factory(
      servername, auth_func, GetUserAgent(), GetSourceName(),
      extra_headers=extra_headers, save_cookies=save_cookies,
      auth_tries=auth_tries, debug_data=False, secure=secure,
      ignore_certs=True)
  if not app_id:
    app_id = GetRemoteAppIdFromServer(server, path, rtok)

  ConfigureRemoteApiFromServer(
      server, path, app_id, services=services, apiproxy=apiproxy,
      default_auth_domain=default_auth_domain,
      use_remote_datastore=use_remote_datastore,
      **kwargs)
  return server


def MaybeInvokeAuthentication():
  """Sends an empty request through to the configured end-point.

  If authentication is necessary, this will cause the rpc_server to invoke
  interactive authentication.
  """
  datastore_stub = apiproxy_stub_map.apiproxy.GetStub('datastore_v3')
  if isinstance(datastore_stub, RemoteStub):
    datastore_stub._server.Send(datastore_stub._path, payload=None)
  else:
    raise ConfigurationError('remote_api is not configured.')



ConfigureRemoteDatastore = ConfigureRemoteApi
