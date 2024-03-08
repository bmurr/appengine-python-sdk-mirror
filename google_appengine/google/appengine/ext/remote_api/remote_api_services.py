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


"""Service configuration for remote API.

This module is shared by both the remote_api_stub and the handler.
"""

import six
from google.appengine.api import api_base_pb2
from google.appengine.api import mail_service_pb2
from google.appengine.api import mail_stub_service_pb2
from google.appengine.api import urlfetch_service_pb2
from google.appengine.api import urlfetch_stub_service_pb2
from google.appengine.api import user_service_pb2
from google.appengine.api import user_stub_service_pb2
from google.appengine.api.app_identity import app_identity_service_pb2
from google.appengine.api.app_identity import app_identity_stub_service_pb2
from google.appengine.api.blobstore import blobstore_service_pb2
from google.appengine.api.blobstore import blobstore_stub_service_pb2
from google.appengine.api.capabilities import capability_service_pb2
from google.appengine.api.capabilities import capability_stub_service_pb2
from google.appengine.api.images import images_service_pb2
from google.appengine.api.logservice import log_service_pb2
from google.appengine.api.logservice import log_stub_service_pb2
from google.appengine.api.memcache import memcache_service_pb2
from google.appengine.api.memcache import memcache_stub_service_pb2
from google.appengine.api.modules import modules_service_pb2
from google.appengine.api.search import search_service_pb2
from google.appengine.api.system import system_service_pb2
from google.appengine.api.taskqueue import taskqueue_service_bytes_pb2 as taskqueue_service_pb2
from google.appengine.api.taskqueue import taskqueue_stub_service_bytes_pb2 as taskqueue_stub_service_pb2
from google.appengine.datastore import datastore_pb
from google.appengine.datastore import datastore_v4_pb2
from google.appengine.ext.remote_api import remote_api_bytes_pb2 as remote_api_pb2


def get_service_pb_map():
  """Returns a mapping of all API services defined for prod Remote API use."""
  return {
      'app_identity_service': {
          'SignForApp': (app_identity_service_pb2.SignForAppRequest,
                         app_identity_service_pb2.SignForAppResponse),
          'GetPublicCertificatesForApp':
              (app_identity_service_pb2.GetPublicCertificateForAppRequest,
               app_identity_service_pb2.GetPublicCertificateForAppResponse),
          'GetServiceAccountName':
              (app_identity_service_pb2.GetServiceAccountNameRequest,
               app_identity_service_pb2.GetServiceAccountNameResponse),
          'GetDefaultGcsBucketName':
              (app_identity_service_pb2.GetDefaultGcsBucketNameRequest,
               app_identity_service_pb2.GetDefaultGcsBucketNameResponse),
          'GetAccessToken': (app_identity_service_pb2.GetAccessTokenRequest,
                             app_identity_service_pb2.GetAccessTokenResponse),
      },
      'blobstore': {
          'CreateUploadURL': (blobstore_service_pb2.CreateUploadURLRequest,
                              blobstore_service_pb2.CreateUploadURLResponse),
          'DeleteBlob':
              (blobstore_service_pb2.DeleteBlobRequest, api_base_pb2.VoidProto),
          'FetchData': (blobstore_service_pb2.FetchDataRequest,
                        blobstore_service_pb2.FetchDataResponse),
          'DecodeBlobKey': (blobstore_service_pb2.DecodeBlobKeyRequest,
                            blobstore_service_pb2.DecodeBlobKeyResponse),
          'CreateEncodedGoogleStorageKey':
              (blobstore_service_pb2.CreateEncodedGoogleStorageKeyRequest,
               blobstore_service_pb2.CreateEncodedGoogleStorageKeyResponse),
      },
      'capability_service': {
          'IsEnabled': (capability_service_pb2.IsEnabledRequest,
                        capability_service_pb2.IsEnabledResponse),
      },
      'datastore_v3': {
          'Get': (datastore_pb.GetRequest, datastore_pb.GetResponse),
          'Put': (datastore_pb.PutRequest, datastore_pb.PutResponse),
          'Delete': (datastore_pb.DeleteRequest, datastore_pb.DeleteResponse),
          'AllocateIds': (datastore_pb.AllocateIdsRequest,
                          datastore_pb.AllocateIdsResponse),
          'RunQuery': (datastore_pb.Query, datastore_pb.QueryResult),
          'Next': (datastore_pb.NextRequest, datastore_pb.QueryResult),
          'BeginTransaction':
              (datastore_pb.BeginTransactionRequest, datastore_pb.Transaction),
          'Commit': (datastore_pb.Transaction, datastore_pb.CommitResponse),
          'Rollback': (datastore_pb.Transaction, api_base_pb2.VoidProto),
          'GetIndices':
              (datastore_pb.GetIndicesRequest, datastore_pb.CompositeIndices),
      },
      'datastore_v4': {
          'AllocateIds': (datastore_v4_pb2.AllocateIdsRequest,
                          datastore_v4_pb2.AllocateIdsResponse),
      },
      'images': {
          'Transform': (images_service_pb2.ImagesTransformRequest,
                        images_service_pb2.ImagesTransformResponse),
          'Composite': (images_service_pb2.ImagesCompositeRequest,
                        images_service_pb2.ImagesCompositeResponse),
          'Histogram': (images_service_pb2.ImagesHistogramRequest,
                        images_service_pb2.ImagesHistogramResponse),
          'GetUrlBase': (images_service_pb2.ImagesGetUrlBaseRequest,
                         images_service_pb2.ImagesGetUrlBaseResponse),
          'DeleteUrlBase': (images_service_pb2.ImagesDeleteUrlBaseRequest,
                            images_service_pb2.ImagesDeleteUrlBaseResponse),
      },
      'logservice': {
          'Flush': (log_service_pb2.FlushRequest, api_base_pb2.VoidProto),
          'Read':
              (log_service_pb2.LogReadRequest, log_service_pb2.LogReadResponse),
      },
      'mail': {
          'Send': (mail_service_pb2.MailMessage, api_base_pb2.VoidProto),
          'SendToAdmins':
              (mail_service_pb2.MailMessage, api_base_pb2.VoidProto),
      },
      'memcache': {
          'Get': (memcache_service_pb2.MemcacheGetRequest,
                  memcache_service_pb2.MemcacheGetResponse),
          'Set': (memcache_service_pb2.MemcacheSetRequest,
                  memcache_service_pb2.MemcacheSetResponse),
          'Delete': (memcache_service_pb2.MemcacheDeleteRequest,
                     memcache_service_pb2.MemcacheDeleteResponse),
          'Increment': (memcache_service_pb2.MemcacheIncrementRequest,
                        memcache_service_pb2.MemcacheIncrementResponse),
          'BatchIncrement':
              (memcache_service_pb2.MemcacheBatchIncrementRequest,
               memcache_service_pb2.MemcacheBatchIncrementResponse),
          'FlushAll': (memcache_service_pb2.MemcacheFlushRequest,
                       memcache_service_pb2.MemcacheFlushResponse),
          'Stats': (memcache_service_pb2.MemcacheStatsRequest,
                    memcache_service_pb2.MemcacheStatsResponse),
      },
      'remote_datastore': {
          'RunQuery': (datastore_pb.Query, datastore_pb.QueryResult),
          'TransactionQuery':
              (datastore_pb.Query, remote_api_pb2.TransactionQueryResult),
          'Transaction':
              (remote_api_pb2.TransactionRequest, datastore_pb.PutResponse),
          'GetIDs': (datastore_pb.PutRequest, datastore_pb.PutResponse),
          'GetIDsXG': (datastore_pb.PutRequest, datastore_pb.PutResponse),
      },
      'search': {
          'IndexDocument': (search_service_pb2.IndexDocumentRequest,
                            search_service_pb2.IndexDocumentResponse),
          'DeleteDocument': (search_service_pb2.DeleteDocumentRequest,
                             search_service_pb2.DeleteDocumentResponse),
          'ListDocuments': (search_service_pb2.ListDocumentsRequest,
                            search_service_pb2.ListDocumentsResponse),
          'ListIndexes': (search_service_pb2.ListIndexesRequest,
                          search_service_pb2.ListIndexesResponse),
          'Search': (search_service_pb2.SearchRequest,
                     search_service_pb2.SearchResponse),
          'DeleteSchema': (search_service_pb2.DeleteSchemaRequest,
                           search_service_pb2.DeleteSchemaResponse),
      },
      'modules': {
          'GetModules': (modules_service_pb2.GetModulesRequest,
                         modules_service_pb2.GetModulesResponse),
          'GetVersions': (modules_service_pb2.GetVersionsRequest,
                          modules_service_pb2.GetVersionsResponse),
          'GetDefaultVersion': (modules_service_pb2.GetDefaultVersionRequest,
                                modules_service_pb2.GetDefaultVersionResponse),
          'GetNumInstances': (modules_service_pb2.GetNumInstancesRequest,
                              modules_service_pb2.GetNumInstancesResponse),
          'SetNumInstances': (modules_service_pb2.SetNumInstancesRequest,
                              modules_service_pb2.SetNumInstancesResponse),
          'StartModule': (modules_service_pb2.StartModuleRequest,
                          modules_service_pb2.StartModuleResponse),
          'StopModule': (modules_service_pb2.StopModuleRequest,
                         modules_service_pb2.StopModuleResponse),
          'GetHostname': (modules_service_pb2.GetHostnameRequest,
                          modules_service_pb2.GetHostnameResponse),
      },
      'system': {
          'GetSystemStats': (system_service_pb2.GetSystemStatsRequest,
                             system_service_pb2.GetSystemStatsResponse),
          'StartBackgroundRequest':
              (system_service_pb2.StartBackgroundRequestRequest,
               system_service_pb2.StartBackgroundRequestResponse),
      },
      'taskqueue': {
          'Add': (taskqueue_service_pb2.TaskQueueAddRequest,
                  taskqueue_service_pb2.TaskQueueAddResponse),
          'BulkAdd': (taskqueue_service_pb2.TaskQueueBulkAddRequest,
                      taskqueue_service_pb2.TaskQueueBulkAddResponse),
          'FetchQueues': (taskqueue_service_pb2.TaskQueueFetchQueuesRequest,
                          taskqueue_service_pb2.TaskQueueFetchQueuesResponse),
          'FetchQueueStats':
              (taskqueue_service_pb2.TaskQueueFetchQueueStatsRequest,
               taskqueue_service_pb2.TaskQueueFetchQueueStatsResponse),
          'Delete': (taskqueue_service_pb2.TaskQueueDeleteRequest,
                     taskqueue_service_pb2.TaskQueueDeleteResponse),
          'ForceRun': (taskqueue_service_pb2.TaskQueueForceRunRequest,
                       taskqueue_service_pb2.TaskQueueForceRunResponse),
          'UpdateQueue': (taskqueue_service_pb2.TaskQueueUpdateQueueRequest,
                          taskqueue_service_pb2.TaskQueueUpdateQueueResponse),
          'PauseQueue': (taskqueue_service_pb2.TaskQueuePauseQueueRequest,
                         taskqueue_service_pb2.TaskQueuePauseQueueResponse),
          'PurgeQueue': (taskqueue_service_pb2.TaskQueuePurgeQueueRequest,
                         taskqueue_service_pb2.TaskQueuePurgeQueueResponse),
          'DeleteQueue': (taskqueue_service_pb2.TaskQueueDeleteQueueRequest,
                          taskqueue_service_pb2.TaskQueueDeleteQueueResponse),
          'DeleteGroup': (taskqueue_service_pb2.TaskQueueDeleteGroupRequest,
                          taskqueue_service_pb2.TaskQueueDeleteGroupResponse),
          'QueryTasks': (taskqueue_service_pb2.TaskQueueQueryTasksRequest,
                         taskqueue_service_pb2.TaskQueueQueryTasksResponse),
          'FetchTask': (taskqueue_service_pb2.TaskQueueFetchTaskRequest,
                        taskqueue_service_pb2.TaskQueueFetchTaskResponse),
          'QueryAndOwnTasks':
              (taskqueue_service_pb2.TaskQueueQueryAndOwnTasksRequest,
               taskqueue_service_pb2.TaskQueueQueryAndOwnTasksResponse),
          'ModifyTaskLease':
              (taskqueue_service_pb2.TaskQueueModifyTaskLeaseRequest,
               taskqueue_service_pb2.TaskQueueModifyTaskLeaseResponse),
          'UpdateStorageLimit':
              (taskqueue_service_pb2.TaskQueueUpdateStorageLimitRequest,
               taskqueue_service_pb2.TaskQueueUpdateStorageLimitResponse),
      },
      'urlfetch': {
          'Fetch': (urlfetch_service_pb2.URLFetchRequest,
                    urlfetch_service_pb2.URLFetchResponse),
      },
      'user': {
          'CreateLoginURL': (user_service_pb2.CreateLoginURLRequest,
                             user_service_pb2.CreateLoginURLResponse),
          'CreateLogoutURL': (user_service_pb2.CreateLogoutURLRequest,
                              user_service_pb2.CreateLogoutURLResponse),
          'GetOAuthUser': (user_service_pb2.GetOAuthUserRequest,
                           user_service_pb2.GetOAuthUserResponse),
      },
  }


def get_stub_exclusive_service_pb_map():
  """Returns all API services exclusively for local use."""
  return {
      'app_identity_service': {
          'SetDefaultGcsBucketName': (
              app_identity_stub_service_pb2.SetDefaultGcsBucketNameRequest,
              api_base_pb2.VoidProto),
      },
      'blobstore': {
          'StoreBlob': (blobstore_stub_service_pb2.StoreBlobRequest,
                        api_base_pb2.VoidProto),
          'SetBlobStorageType': (
              blobstore_stub_service_pb2.SetBlobStorageTypeRequest,
              api_base_pb2.VoidProto),
      },
      'capability_service': {
          'SetCapabilityStatus': (
              capability_stub_service_pb2.SetCapabilityStatusRequest,
              capability_stub_service_pb2.SetCapabilityStatusResponse),
      },
      'logservice': {
          'AddAppLogLine': (log_stub_service_pb2.AddAppLogLineRequest,
                            api_base_pb2.VoidProto),
          'AddRequestInfo': (log_stub_service_pb2.AddRequestInfoRequest,
                             api_base_pb2.VoidProto),
          'EndRequestLog': (log_stub_service_pb2.EndRequestLogRequest,
                            api_base_pb2.VoidProto),
          'StartRequestLog': (log_stub_service_pb2.StartRequestLogRequest,
                              api_base_pb2.VoidProto)
      },
      'mail': {
          'GetSentMessages': (api_base_pb2.VoidProto,
                              mail_stub_service_pb2.GetSentMessagesResponse),
          'ClearSentMessages': (
              api_base_pb2.VoidProto,
              mail_stub_service_pb2.ClearSentMessagesResponse),
          'GetLogMailBody': (api_base_pb2.VoidProto,
                             mail_stub_service_pb2.GetLogMailBodyResponse),
          'SetLogMailBody': (mail_stub_service_pb2.SetLogMailBodyRequest,
                             api_base_pb2.VoidProto),
          'GetLogMailLevel': (api_base_pb2.VoidProto,
                              mail_stub_service_pb2.GetLogMailLevelResponse),
          'SetLogMailLevel': (mail_stub_service_pb2.SetLogMailLevelRequest,
                              api_base_pb2.VoidProto),
      },
      'memcache': {
          'AdvanceClock': (memcache_stub_service_pb2.AdvanceClockRequest,
                           memcache_stub_service_pb2.AdvanceClockResponse),
          'SetClock': (memcache_stub_service_pb2.SetClockRequest,
                       api_base_pb2.VoidProto),
          'GetLruChainLength': (
              api_base_pb2.VoidProto,
              memcache_stub_service_pb2.GetLruChainLengthResponse),
          'SetMaxSize': (memcache_stub_service_pb2.SetMaxSizeRequest,
                         api_base_pb2.VoidProto),
      },
      'taskqueue': {
          'SetUpStub': (taskqueue_stub_service_pb2.SetUpStubRequest,
                        api_base_pb2.VoidProto),
          'GetQueues': (api_base_pb2.VoidProto,
                        taskqueue_stub_service_pb2.GetQueuesResponse),
          'DeleteTask': (taskqueue_service_pb2.TaskQueueDeleteRequest,
                         api_base_pb2.VoidProto),
          'FlushQueue': (taskqueue_stub_service_pb2.FlushQueueRequest,
                         api_base_pb2.VoidProto),
          'GetFilteredTasks': (
              taskqueue_stub_service_pb2.GetFilteredTasksRequest,
              taskqueue_stub_service_pb2.GetFilteredTasksResponse),
          'GetQueueStateInfo': (
              api_base_pb2.VoidProto,
              taskqueue_stub_service_pb2.GetQueueStateInfoResponse),
          'LoadQueueXml': (taskqueue_stub_service_pb2.LoadQueueXmlRequest,
                           api_base_pb2.VoidProto),
          'SetTaskQueueClock': (
              taskqueue_stub_service_pb2.SetTaskQueueClockRequest,
              api_base_pb2.VoidProto),
          'PatchQueueYamlParser': (
              taskqueue_stub_service_pb2.PatchQueueYamlParserRequest,
              api_base_pb2.VoidProto),
      },
      'urlfetch': {
          'SetHttpProxy': (urlfetch_stub_service_pb2.SetHttpProxyRequest,
                           api_base_pb2.VoidProto),
      },
      'user': {
          'SetOAuthUser': (user_stub_service_pb2.SetOAuthUserRequest,
                           api_base_pb2.VoidProto),
      }
  }


def get_stub_service_pb_map():
  """Returns a mapping of all API services defined for local Remote API use.

  This contains all services defined in get_service_pb_map, and is extended with
  additional services defined by get_stub_exclusive_service_pb_map.
  """
  service_pb_map = get_service_pb_map()
  stub_exclusive_services = get_stub_exclusive_service_pb_map()

  for stub, services in six.iteritems(service_pb_map):
    services.update(stub_exclusive_services.get(stub, {}))

  return service_pb_map


SERVICE_PB_MAP = get_service_pb_map()
STUB_SERVICE_PB_MAP = get_stub_service_pb_map()
