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
    'google/appengine/tools/devappserver2/runtime_config.proto'
)


_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n9google/appengine/tools/devappserver2/runtime_config.proto\x12$google.appengine.tools.devappserver2\"\xaa\x08\n\x06\x43onfig\x12\x0e\n\x06\x61pp_id\x18\x01 \x01(\x0c\x12\x12\n\nversion_id\x18\x02 \x01(\x0c\x12\x18\n\x10\x61pplication_root\x18\x03 \x01(\x0c\x12\x19\n\nthreadsafe\x18\x04 \x01(\x08:\x05\x66\x61lse\x12\x1b\n\x08\x61pi_host\x18\x11 \x01(\t:\tlocalhost\x12\x10\n\x08\x61pi_port\x18\x05 \x01(\x05\x12@\n\tlibraries\x18\x06 \x03(\x0b\x32-.google.appengine.tools.devappserver2.Library\x12\x16\n\nskip_files\x18\x07 \x01(\t:\x02^$\x12\x18\n\x0cstatic_files\x18\x08 \x01(\t:\x02^$\x12I\n\rpython_config\x18\x0e \x01(\x0b\x32\x32.google.appengine.tools.devappserver2.PythonConfig\x12\x43\n\nphp_config\x18\t \x01(\x0b\x32/.google.appengine.tools.devappserver2.PhpConfig\x12\x45\n\x0bnode_config\x18\x1a \x01(\x0b\x32\x30.google.appengine.tools.devappserver2.NodeConfig\x12\x45\n\x0bjava_config\x18\x15 \x01(\x0b\x32\x30.google.appengine.tools.devappserver2.JavaConfig\x12I\n\rcustom_config\x18\x17 \x01(\x0b\x32\x32.google.appengine.tools.devappserver2.CustomConfig\x12\x41\n\tgo_config\x18\x19 \x01(\x0b\x32..google.appengine.tools.devappserver2.GoConfig\x12>\n\x07\x65nviron\x18\n \x03(\x0b\x32-.google.appengine.tools.devappserver2.Environ\x12H\n\x10\x63loud_sql_config\x18\x0b \x01(\x0b\x32..google.appengine.tools.devappserver2.CloudSQL\x12\x12\n\ndatacenter\x18\x0c \x01(\t\x12\x13\n\x0binstance_id\x18\r \x01(\t\x12\x1b\n\x10stderr_log_level\x18\x0f \x01(\x03:\x01\x31\x12\x13\n\x0b\x61uth_domain\x18\x10 \x01(\t\x12\x15\n\rmax_instances\x18\x12 \x01(\x05\x12\x41\n\tvm_config\x18\x13 \x01(\x0b\x32..google.appengine.tools.devappserver2.VMConfig\x12\x13\n\x0bserver_port\x18\x14 \x01(\x05\x12\x11\n\x02vm\x18\x16 \x01(\x08:\x05\x66\x61lse\x12\x11\n\tgrpc_apis\x18\x18 \x03(\t\"\xc6\x01\n\tPhpConfig\x12\x1b\n\x13php_executable_path\x18\x01 \x01(\x0c\x12\x17\n\x0f\x65nable_debugger\x18\x03 \x01(\x08\x12\x1a\n\x12gae_extension_path\x18\x04 \x01(\x0c\x12\x1d\n\x15xdebug_extension_path\x18\x05 \x01(\x0c\x12\x13\n\x0bphp_version\x18\x06 \x01(\x0c\x12\x18\n\x10php_library_path\x18\x07 \x01(\x0c\x12\x19\n\x11php_composer_path\x18\x08 \x01(\x0c\"*\n\nNodeConfig\x12\x1c\n\x14node_executable_path\x18\x01 \x01(\x0c\"<\n\x0cPythonConfig\x12\x16\n\x0estartup_script\x18\x01 \x01(\t\x12\x14\n\x0cstartup_args\x18\x02 \x01(\t\"\x1e\n\nJavaConfig\x12\x10\n\x08jvm_args\x18\x01 \x03(\t\"W\n\x08GoConfig\x12\x10\n\x08work_dir\x18\x01 \x01(\t\x12\x1f\n\x17\x65nable_watching_go_path\x18\x02 \x01(\x08\x12\x18\n\x10\x65nable_debugging\x18\x03 \x01(\x08\":\n\x0c\x43ustomConfig\x12\x19\n\x11\x63ustom_entrypoint\x18\x01 \x01(\t\x12\x0f\n\x07runtime\x18\x02 \x01(\t\"t\n\x08\x43loudSQL\x12\x12\n\nmysql_host\x18\x01 \x01(\t\x12\x12\n\nmysql_port\x18\x02 \x01(\x05\x12\x12\n\nmysql_user\x18\x03 \x01(\t\x12\x16\n\x0emysql_password\x18\x04 \x01(\t\x12\x14\n\x0cmysql_socket\x18\x05 \x01(\t\"(\n\x07Library\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"%\n\x07\x45nviron\x12\x0b\n\x03key\x18\x01 \x01(\x0c\x12\r\n\x05value\x18\x02 \x01(\x0c\":\n\x08VMConfig\x12\x19\n\x11\x64ocker_daemon_url\x18\x01 \x01(\t\x12\x13\n\x0b\x65nable_logs\x18\x03 \x01(\x08\x42\x30\n,com.google.appengine.tools.development.protoP\x01')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.appengine.tools.devappserver2.runtime_config_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n,com.google.appengine.tools.development.protoP\001'
  _globals['_CONFIG']._serialized_start=100
  _globals['_CONFIG']._serialized_end=1166
  _globals['_PHPCONFIG']._serialized_start=1169
  _globals['_PHPCONFIG']._serialized_end=1367
  _globals['_NODECONFIG']._serialized_start=1369
  _globals['_NODECONFIG']._serialized_end=1411
  _globals['_PYTHONCONFIG']._serialized_start=1413
  _globals['_PYTHONCONFIG']._serialized_end=1473
  _globals['_JAVACONFIG']._serialized_start=1475
  _globals['_JAVACONFIG']._serialized_end=1505
  _globals['_GOCONFIG']._serialized_start=1507
  _globals['_GOCONFIG']._serialized_end=1594
  _globals['_CUSTOMCONFIG']._serialized_start=1596
  _globals['_CUSTOMCONFIG']._serialized_end=1654
  _globals['_CLOUDSQL']._serialized_start=1656
  _globals['_CLOUDSQL']._serialized_end=1772
  _globals['_LIBRARY']._serialized_start=1774
  _globals['_LIBRARY']._serialized_end=1814
  _globals['_ENVIRON']._serialized_start=1816
  _globals['_ENVIRON']._serialized_end=1853
  _globals['_VMCONFIG']._serialized_start=1855
  _globals['_VMCONFIG']._serialized_end=1913

