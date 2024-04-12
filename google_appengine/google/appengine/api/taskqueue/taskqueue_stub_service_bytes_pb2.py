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





"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    0,
    '-dev',
    'google/appengine/api/taskqueue/taskqueue_stub_service_bytes.proto'
)


_sym_db = _symbol_database.Default()


from google.appengine.api import api_base_pb2 as google_dot_appengine_dot_api_dot_api__base__pb2
from google.appengine.api.taskqueue import taskqueue_service_bytes_pb2 as google_dot_appengine_dot_api_dot_taskqueue_dot_taskqueue__service__bytes__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nAgoogle/appengine/api/taskqueue/taskqueue_stub_service_bytes.proto\x12\x10\x61pphosting_bytes\x1a#google/appengine/api/api_base.proto\x1a<google/appengine/api/taskqueue/taskqueue_service_bytes.proto\"\xba\x01\n\x11GetQueuesResponse\x12M\n\x15\x66\x65tch_queues_response\x18\x01 \x01(\x0b\x32..apphosting_bytes.TaskQueueFetchQueuesResponse\x12V\n\x1a\x66\x65tch_queue_stats_response\x18\x02 \x01(\x0b\x32\x32.apphosting_bytes.TaskQueueFetchQueueStatsResponse\"z\n\x18GetFilteredTasksResponse\x12K\n\x14query_tasks_response\x18\x01 \x01(\x0b\x32-.apphosting_bytes.TaskQueueQueryTasksResponse\x12\x11\n\teta_delta\x18\x02 \x03(\t\"\'\n\x11\x46lushQueueRequest\x12\x12\n\nqueue_name\x18\x01 \x01(\t\"I\n\x17GetFilteredTasksRequest\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bqueue_names\x18\x03 \x03(\t\";\n\x1bPatchQueueYamlParserRequest\x12\x1c\n\x14patched_return_value\x18\x01 \x01(\t\"\xf0\x01\n\x10SetUpStubRequest\x12\x14\n\x0cservice_name\x18\x01 \x01(\t\x12\x11\n\troot_path\x18\x02 \x01(\t\x12\x19\n\x11\x61uto_task_running\x18\x03 \x01(\x08\x12\x1a\n\x12task_retry_seconds\x18\x04 \x01(\x05\x12\x18\n\x10\x61ll_queues_valid\x18\x05 \x01(\x08\x12\x1b\n\x13\x64\x65\x66\x61ult_http_server\x18\x06 \x01(\t\x12\x1e\n\x16testing_validate_state\x18\x07 \x01(\x08\x12\x14\n\x0crequest_data\x18\x08 \x01(\x0c\x12\x0f\n\x07gettime\x18\t \x01(\t\"\xad\x04\n\x19GetQueueStateInfoResponse\x12\x45\n\x06queues\x18\x01 \x03(\x0b\x32\x35.apphosting_bytes.GetQueueStateInfoResponse.QueueInfo\x1a\xc8\x03\n\tQueueInfo\x12\x12\n\nqueue_name\x18\x01 \x01(\t\x12\x1d\n\x15\x66ormatted_rate_string\x18\x02 \x01(\t\x12\x13\n\x0b\x62ucket_size\x18\x03 \x01(\x05\x12\x1f\n\x17max_concurrent_requests\x18\x04 \x01(\x05\x12\x44\n\x10retry_parameters\x18\x05 \x01(\x0b\x32*.apphosting_bytes.TaskQueueRetryParameters\x12\x0e\n\x06target\x18\x06 \x01(\t\x12\x0c\n\x04mode\x18\x07 \x01(\t\x12+\n\x03\x61\x63l\x18\x08 \x01(\x0b\x32\x1e.apphosting_bytes.TaskQueueAcl\x12R\n\ntask_infos\x18\t \x03(\x0b\x32>.apphosting_bytes.GetQueueStateInfoResponse.QueueInfo.TaskInfo\x1am\n\x08TaskInfo\x12\x11\n\ttask_name\x18\x01 \x01(\t\x12\x12\n\neta_millis\x18\x02 \x01(\x03\x12:\n\x0b\x61\x64\x64_request\x18\x03 \x01(\x0b\x32%.apphosting_bytes.TaskQueueAddRequest\"-\n\x13LoadQueueXmlRequest\x12\x16\n\x0equeue_xml_path\x18\x01 \x01(\t\";\n\x18SetTaskQueueClockRequest\x12\x1f\n\x17\x63lock_time_milliseconds\x18\x01 \x01(\x03\x42<\n\"com.google.appengine.api.taskqueueB\x16TaskQueueStubServicePb')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.appengine.api.taskqueue.taskqueue_stub_service_bytes_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\"com.google.appengine.api.taskqueueB\026TaskQueueStubServicePb'
  _globals['_GETQUEUESRESPONSE']._serialized_start=187
  _globals['_GETQUEUESRESPONSE']._serialized_end=373
  _globals['_GETFILTEREDTASKSRESPONSE']._serialized_start=375
  _globals['_GETFILTEREDTASKSRESPONSE']._serialized_end=497
  _globals['_FLUSHQUEUEREQUEST']._serialized_start=499
  _globals['_FLUSHQUEUEREQUEST']._serialized_end=538
  _globals['_GETFILTEREDTASKSREQUEST']._serialized_start=540
  _globals['_GETFILTEREDTASKSREQUEST']._serialized_end=613
  _globals['_PATCHQUEUEYAMLPARSERREQUEST']._serialized_start=615
  _globals['_PATCHQUEUEYAMLPARSERREQUEST']._serialized_end=674
  _globals['_SETUPSTUBREQUEST']._serialized_start=677
  _globals['_SETUPSTUBREQUEST']._serialized_end=917
  _globals['_GETQUEUESTATEINFORESPONSE']._serialized_start=920
  _globals['_GETQUEUESTATEINFORESPONSE']._serialized_end=1477
  _globals['_GETQUEUESTATEINFORESPONSE_QUEUEINFO']._serialized_start=1021
  _globals['_GETQUEUESTATEINFORESPONSE_QUEUEINFO']._serialized_end=1477
  _globals['_GETQUEUESTATEINFORESPONSE_QUEUEINFO_TASKINFO']._serialized_start=1368
  _globals['_GETQUEUESTATEINFORESPONSE_QUEUEINFO_TASKINFO']._serialized_end=1477
  _globals['_LOADQUEUEXMLREQUEST']._serialized_start=1479
  _globals['_LOADQUEUEXMLREQUEST']._serialized_end=1524
  _globals['_SETTASKQUEUECLOCKREQUEST']._serialized_start=1526
  _globals['_SETTASKQUEUECLOCKREQUEST']._serialized_end=1585

