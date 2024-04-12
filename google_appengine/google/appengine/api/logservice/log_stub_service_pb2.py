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
    'google/appengine/api/logservice/log_stub_service.proto'
)


_sym_db = _symbol_database.Default()


from google.appengine.api import api_base_pb2 as google_dot_appengine_dot_api_dot_api__base__pb2
from google.appengine.api.logservice import log_service_pb2 as google_dot_appengine_dot_api_dot_logservice_dot_log__service__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n6google/appengine/api/logservice/log_stub_service.proto\x12\x10google.appengine\x1a#google/appengine/api/api_base.proto\x1a\x31google/appengine/api/logservice/log_service.proto\"J\n\x15\x41\x64\x64RequestInfoRequest\x12\x31\n\x0brequest_log\x18\x01 \x01(\x0b\x32\x1c.google.appengine.RequestLog\"W\n\x14\x41\x64\x64\x41ppLogLineRequest\x12+\n\x08log_line\x18\x01 \x01(\x0b\x32\x19.google.appengine.LogLine\x12\x12\n\nrequest_id\x18\x02 \x01(\t\"\x85\x02\n\x16StartRequestLogRequest\x12\x12\n\nrequest_id\x18\x01 \x01(\t\x12\x17\n\x0fuser_request_id\x18\x02 \x01(\t\x12\n\n\x02ip\x18\x03 \x01(\t\x12\x0e\n\x06\x61pp_id\x18\x04 \x01(\t\x12\x12\n\nversion_id\x18\x05 \x01(\t\x12\x10\n\x08nickname\x18\x06 \x01(\t\x12\x12\n\nuser_agent\x18\x07 \x01(\t\x12\x0c\n\x04host\x18\x08 \x01(\t\x12\x0e\n\x06method\x18\t \x01(\t\x12\x10\n\x08resource\x18\n \x01(\t\x12\x14\n\x0chttp_version\x18\x0b \x01(\t\x12\x12\n\nstart_time\x18\x0c \x01(\x03\x12\x0e\n\x06module\x18\r \x01(\t\"Q\n\x14\x45ndRequestLogRequest\x12\x12\n\nrequest_id\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\x05\x12\x15\n\rresponse_size\x18\x03 \x01(\x05')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.appengine.api.logservice.log_stub_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ADDREQUESTINFOREQUEST']._serialized_start=164
  _globals['_ADDREQUESTINFOREQUEST']._serialized_end=238
  _globals['_ADDAPPLOGLINEREQUEST']._serialized_start=240
  _globals['_ADDAPPLOGLINEREQUEST']._serialized_end=327
  _globals['_STARTREQUESTLOGREQUEST']._serialized_start=330
  _globals['_STARTREQUESTLOGREQUEST']._serialized_end=591
  _globals['_ENDREQUESTLOGREQUEST']._serialized_start=593
  _globals['_ENDREQUESTLOGREQUEST']._serialized_end=674

