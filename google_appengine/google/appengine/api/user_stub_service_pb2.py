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
    'google/appengine/api/user_stub_service.proto'
)


_sym_db = _symbol_database.Default()


from google.appengine.api import api_base_pb2 as google_dot_appengine_dot_api_dot_api__base__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n,google/appengine/api/user_stub_service.proto\x12\x10google.appengine\x1a#google/appengine/api/api_base.proto\"\x7f\n\x13SetOAuthUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x13\n\x0b\x61uth_domain\x18\x02 \x01(\t\x12\x0f\n\x07user_id\x18\x03 \x01(\t\x12\x10\n\x08is_admin\x18\x04 \x01(\x08\x12\x0e\n\x06scopes\x18\x05 \x03(\t\x12\x11\n\tclient_id\x18\x06 \x01(\tB4\n\x1f\x63om.google.google.appengine.apiB\x11UserStubServicePb')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.appengine.api.user_stub_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\037com.google.google.appengine.apiB\021UserStubServicePb'
  _globals['_SETOAUTHUSERREQUEST']._serialized_start=103
  _globals['_SETOAUTHUSERREQUEST']._serialized_end=230

