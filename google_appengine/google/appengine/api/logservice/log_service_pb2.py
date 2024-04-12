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
    'google/appengine/api/logservice/log_service.proto'
)


_sym_db = _symbol_database.Default()


from google.appengine.api import source_pb2 as google_dot_appengine_dot_api_dot_source__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n1google/appengine/api/logservice/log_service.proto\x12\x10google.appengine\x1a!google/appengine/api/source.proto\"N\n\x0fLogServiceError\";\n\tErrorCode\x12\x06\n\x02OK\x10\x00\x12\x13\n\x0fINVALID_REQUEST\x10\x01\x12\x11\n\rSTORAGE_ERROR\x10\x02\"\x83\x01\n\x0eUserAppLogLine\x12\x16\n\x0etimestamp_usec\x18\x01 \x01(\x03\x12\r\n\x05level\x18\x02 \x01(\x03\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\x39\n\x0fsource_location\x18\x04 \x01(\x0b\x32 .google.appengine.SourceLocation\"E\n\x0fUserAppLogGroup\x12\x32\n\x08log_line\x18\x02 \x03(\x0b\x32 .google.appengine.UserAppLogLine\"\x1c\n\x0c\x46lushRequest\x12\x0c\n\x04logs\x18\x01 \x01(\x0c\"B\n\tLogOffset\x12\x12\n\nrequest_id\x18\x01 \x01(\x0c\x12!\n\x19\x64\x65precated_request_id_set\x18\x65 \x01(\x08\"v\n\x07LogLine\x12\x0c\n\x04time\x18\x01 \x01(\x03\x12\r\n\x05level\x18\x02 \x01(\x05\x12\x13\n\x0blog_message\x18\x03 \x01(\t\x12\x39\n\x0fsource_location\x18\x04 \x01(\x0b\x32 .google.appengine.SourceLocation\"\xe0\x07\n\nRequestLog\x12\x0e\n\x06\x61pp_id\x18\x01 \x01(\t\x12\x1a\n\tmodule_id\x18% \x01(\t:\x07\x64\x65\x66\x61ult\x12\x12\n\nversion_id\x18\x02 \x01(\t\x12\x12\n\nrequest_id\x18\x03 \x01(\x0c\x12+\n\x06offset\x18# \x01(\x0b\x32\x1b.google.appengine.LogOffset\x12\n\n\x02ip\x18\x04 \x01(\t\x12\x10\n\x08nickname\x18\x05 \x01(\t\x12\x12\n\nstart_time\x18\x06 \x01(\x03\x12\x10\n\x08\x65nd_time\x18\x07 \x01(\x03\x12\x0f\n\x07latency\x18\x08 \x01(\x03\x12\x0f\n\x07mcycles\x18\t \x01(\x03\x12\x0e\n\x06method\x18\n \x01(\t\x12\x10\n\x08resource\x18\x0b \x01(\t\x12\x14\n\x0chttp_version\x18\x0c \x01(\t\x12\x0e\n\x06status\x18\r \x01(\x05\x12\x15\n\rresponse_size\x18\x0e \x01(\x03\x12\x10\n\x08referrer\x18\x0f \x01(\t\x12\x12\n\nuser_agent\x18\x10 \x01(\t\x12\x15\n\rurl_map_entry\x18\x11 \x01(\t\x12\x10\n\x08\x63ombined\x18\x12 \x01(\t\x12\x13\n\x0b\x61pi_mcycles\x18\x13 \x01(\x03\x12\x0c\n\x04host\x18\x14 \x01(\t\x12\x17\n\x0ftask_queue_name\x18\x16 \x01(\t\x12\x11\n\ttask_name\x18\x17 \x01(\t\x12\x1b\n\x13was_loading_request\x18\x18 \x01(\x08\x12\x14\n\x0cpending_time\x18\x19 \x01(\x03\x12\x19\n\rreplica_index\x18\x1a \x01(\x05:\x02-1\x12\x16\n\x08\x66inished\x18\x1b \x01(\x08:\x04true\x12\x11\n\tclone_key\x18\x1c \x01(\x0c\x12\'\n\x04line\x18\x1d \x03(\x0b\x32\x19.google.appengine.LogLine\x12\x18\n\x10lines_incomplete\x18$ \x01(\x08\x12\x1a\n\x12\x61pp_engine_release\x18& \x01(\x0c\x12\x10\n\x08trace_id\x18\' \x01(\t\x12\x0f\n\x07span_id\x18( \x01(\t\x12:\n\x06labels\x18) \x03(\x0b\x32*.google.appengine.RequestLog.MapFieldEntry\x12\x13\n\x0b\x65xit_reason\x18\x1e \x01(\x05\x12\x1e\n\x16was_throttled_for_time\x18\x1f \x01(\x08\x12\"\n\x1awas_throttled_for_requests\x18  \x01(\x08\x12\x16\n\x0ethrottled_time\x18! \x01(\x03\x12\x13\n\x0bserver_name\x18\" \x01(\x0c\x1a+\n\rMapFieldEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\tJ\x04\x08\x15\x10\x16\"\x87\x01\n\x10LogModuleVersion\x12\x1a\n\tmodule_id\x18\x01 \x01(\t:\x07\x64\x65\x66\x61ult\x12\x12\n\nversion_id\x18\x02 \x01(\t\x12 \n\x18\x64\x65precated_module_id_set\x18\x65 \x01(\x08\x12!\n\x19\x64\x65precated_version_id_set\x18\x66 \x01(\x08\"\xc3\x06\n\x0eLogReadRequest\x12\x0e\n\x06\x61pp_id\x18\x01 \x01(\t\x12\x12\n\nversion_id\x18\x02 \x03(\t\x12:\n\x0emodule_version\x18\x13 \x03(\x0b\x32\".google.appengine.LogModuleVersion\x12\x12\n\nstart_time\x18\x03 \x01(\x03\x12\x10\n\x08\x65nd_time\x18\x04 \x01(\x03\x12+\n\x06offset\x18\x05 \x01(\x0b\x32\x1b.google.appengine.LogOffset\x12\x12\n\nrequest_id\x18\x06 \x03(\x0c\x12\x19\n\x11minimum_log_level\x18\x07 \x01(\x05\x12\x1a\n\x12include_incomplete\x18\x08 \x01(\x08\x12\r\n\x05\x63ount\x18\t \x01(\x03\x12\x1a\n\x12\x63ombined_log_regex\x18\x0e \x01(\t\x12\x12\n\nhost_regex\x18\x0f \x01(\t\x12\x15\n\rreplica_index\x18\x10 \x01(\x05\x12\x18\n\x10include_app_logs\x18\n \x01(\x08\x12\x1c\n\x14\x61pp_logs_per_request\x18\x11 \x01(\x05\x12\x14\n\x0cinclude_host\x18\x0b \x01(\x08\x12\x13\n\x0binclude_all\x18\x0c \x01(\x08\x12\x16\n\x0e\x63\x61\x63he_iterator\x18\r \x01(\x08\x12\x12\n\nnum_shards\x18\x12 \x01(\x05\x12!\n\x19\x64\x65precated_start_time_set\x18g \x01(\x08\x12\x1f\n\x17\x64\x65precated_end_time_set\x18h \x01(\x08\x12(\n deprecated_minimum_log_level_set\x18k \x01(\x08\x12\x1c\n\x14\x64\x65precated_count_set\x18m \x01(\x08\x12)\n!deprecated_combined_log_regex_set\x18r \x01(\x08\x12!\n\x19\x64\x65precated_host_regex_set\x18s \x01(\x08\x12$\n\x1c\x64\x65precated_replica_index_set\x18t \x01(\x08\x12+\n#deprecated_app_logs_per_request_set\x18u \x01(\x08\x12!\n\x19\x64\x65precated_num_shards_set\x18v \x01(\x08\"\x80\x01\n\x0fLogReadResponse\x12)\n\x03log\x18\x01 \x03(\x0b\x32\x1c.google.appengine.RequestLog\x12+\n\x06offset\x18\x02 \x01(\x0b\x32\x1b.google.appengine.LogOffset\x12\x15\n\rlast_end_time\x18\x03 \x01(\x03\"~\n\x0eLogUsageRecord\x12\x12\n\nversion_id\x18\x01 \x01(\t\x12\x12\n\nstart_time\x18\x02 \x01(\x05\x12\x10\n\x08\x65nd_time\x18\x03 \x01(\x05\x12\r\n\x05\x63ount\x18\x04 \x01(\x03\x12\x12\n\ntotal_size\x18\x05 \x01(\x03\x12\x0f\n\x07records\x18\x06 \x01(\x05\"\x8f\x02\n\x0fLogUsageRequest\x12\x0e\n\x06\x61pp_id\x18\x01 \x01(\t\x12\x12\n\nversion_id\x18\x02 \x03(\t\x12\x12\n\nstart_time\x18\x03 \x01(\x05\x12\x10\n\x08\x65nd_time\x18\x04 \x01(\x05\x12\x1b\n\x10resolution_hours\x18\x05 \x01(\r:\x01\x31\x12\x18\n\x10\x63ombine_versions\x18\x06 \x01(\x08\x12\x15\n\rusage_version\x18\x07 \x01(\x05\x12\x15\n\rversions_only\x18\x08 \x01(\x08\x12\'\n\x1f\x64\x65precated_resolution_hours_set\x18i \x01(\x08\x12$\n\x1c\x64\x65precated_usage_version_set\x18k \x01(\x08\"v\n\x10LogUsageResponse\x12/\n\x05usage\x18\x01 \x03(\x0b\x32 .google.appengine.LogUsageRecord\x12\x31\n\x07summary\x18\x02 \x01(\x0b\x32 .google.appengine.LogUsageRecordB:\n*com.google.google.appengine.api.logserviceB\x0cLogServicePb')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.appengine.api.logservice.log_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n*com.google.google.appengine.api.logserviceB\014LogServicePb'
  _globals['_LOGSERVICEERROR']._serialized_start=106
  _globals['_LOGSERVICEERROR']._serialized_end=184
  _globals['_LOGSERVICEERROR_ERRORCODE']._serialized_start=125
  _globals['_LOGSERVICEERROR_ERRORCODE']._serialized_end=184
  _globals['_USERAPPLOGLINE']._serialized_start=187
  _globals['_USERAPPLOGLINE']._serialized_end=318
  _globals['_USERAPPLOGGROUP']._serialized_start=320
  _globals['_USERAPPLOGGROUP']._serialized_end=389
  _globals['_FLUSHREQUEST']._serialized_start=391
  _globals['_FLUSHREQUEST']._serialized_end=419
  _globals['_LOGOFFSET']._serialized_start=421
  _globals['_LOGOFFSET']._serialized_end=487
  _globals['_LOGLINE']._serialized_start=489
  _globals['_LOGLINE']._serialized_end=607
  _globals['_REQUESTLOG']._serialized_start=610
  _globals['_REQUESTLOG']._serialized_end=1602
  _globals['_REQUESTLOG_MAPFIELDENTRY']._serialized_start=1553
  _globals['_REQUESTLOG_MAPFIELDENTRY']._serialized_end=1596
  _globals['_LOGMODULEVERSION']._serialized_start=1605
  _globals['_LOGMODULEVERSION']._serialized_end=1740
  _globals['_LOGREADREQUEST']._serialized_start=1743
  _globals['_LOGREADREQUEST']._serialized_end=2578
  _globals['_LOGREADRESPONSE']._serialized_start=2581
  _globals['_LOGREADRESPONSE']._serialized_end=2709
  _globals['_LOGUSAGERECORD']._serialized_start=2711
  _globals['_LOGUSAGERECORD']._serialized_end=2837
  _globals['_LOGUSAGEREQUEST']._serialized_start=2840
  _globals['_LOGUSAGEREQUEST']._serialized_end=3111
  _globals['_LOGUSAGERESPONSE']._serialized_start=3113
  _globals['_LOGUSAGERESPONSE']._serialized_end=3231

