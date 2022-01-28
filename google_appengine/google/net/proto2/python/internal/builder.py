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

"""Builds descriptors, message classes and services for generated _pb2.py.

This file is only called in python generated _pb2.py files. It builds
descriptors, message classes and services that users can directly use
in generated code.
"""



from google.net.proto2.python.internal import enum_type_wrapper
from google.net.proto2.python.public import message as _message
from google.net.proto2.python.public import reflection as _reflection
from google.net.proto2.python.public import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()


def BuildMessageAndEnumDescriptors(file_des, module):
  """Builds message and enum descriptors.

  Args:
    file_des: FileDescriptor of the .proto file
    module: Generated _pb2 module
  """

  def BuildNestedDescriptors(msg_des, prefix):
    for (name, nested_msg) in msg_des.nested_types_by_name.items():
      module_name = prefix + name.upper()
      module[module_name] = nested_msg
      BuildNestedDescriptors(nested_msg, module_name + '_')
    for enum_des in msg_des.enum_types:
      module[prefix + enum_des.name.upper()] = enum_des

  for (name, msg_des) in file_des.message_types_by_name.items():
    module_name = '_' + name.upper()
    module[module_name] = msg_des
    BuildNestedDescriptors(msg_des, module_name + '_')


def BuildTopDescriptorsAndMessages(file_des, module_name, module):
  """Builds top level descriptors and message classes.

  Args:
    file_des: FileDescriptor of the .proto file
    module_name: str, the name of generated _pb2 module
    module: Generated _pb2 module
  """

  def BuildMessage(msg_des):
    create_dict = {}
    for (name, nested_msg) in msg_des.nested_types_by_name.items():
      create_dict[name] = BuildMessage(nested_msg)
    create_dict['DESCRIPTOR'] = msg_des
    create_dict['__module__'] = module_name
    message_class = _reflection.GeneratedProtocolMessageType(
        str(msg_des.name), (_message.Message,), create_dict)
    _sym_db.RegisterMessage(message_class)
    return message_class


  for (name, enum_des) in file_des.enum_types_by_name.items():
    module['_' + name.upper()] = enum_des
    module[name] = enum_type_wrapper.EnumTypeWrapper(enum_des)
    for enum_value in enum_des.values:
      module[enum_value.name] = enum_value.number


  for (name, extension_des) in file_des.extensions_by_name.items():
    module[name.upper() + '_FIELD_NUMBER'] = extension_des.number
    module[name] = extension_des


  for (name, service) in file_des.services_by_name.items():
    module['_' + name.upper()] = service


  for (name, msg_des) in file_des.message_types_by_name.items():
    module[name] = BuildMessage(msg_des)


def BuildServices(file_des, module_name, module):
  """Builds services classes and services stub class.

  Args:
    file_des: FileDescriptor of the .proto file
    module_name: str, the name of generated _pb2 module
    module: Generated _pb2 module
  """

  from google.net.proto2.python.public import service as _service
  from google.net.proto2.python.public import service_reflection

  for (name, service) in file_des.services_by_name.items():
    module[name] = service_reflection.GeneratedServiceType(
        name, (_service.Service,),
        dict(DESCRIPTOR=service, __module__=module_name))
    stub_name = name + '_Stub'
    module[stub_name] = service_reflection.GeneratedServiceStubType(
        stub_name, (module[name],),
        dict(DESCRIPTOR=service, __module__=module_name))
