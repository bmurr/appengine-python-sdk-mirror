#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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







"""Contains a metaclass and helper functions used to create
protocol message classes from Descriptor objects at runtime.

Recall that a metaclass is the "type" of a class.
(A class is to a metaclass what an instance is to a class.)

In this case, we use the GeneratedProtocolMessageType metaclass
to inject all the useful functionality into the classes
output by the protocol compiler at compile-time.

The upshot of all this is that the real implementation
details for ALL pure-Python protocol buffers are *here in
this file*.
"""



from io import BytesIO
import struct
import sys
import weakref

from google.appengine._internal import six
from google.appengine._internal.six.moves import range


from google.net.proto2.python.internal import api_implementation
from google.net.proto2.python.internal import containers
from google.net.proto2.python.internal import decoder
from google.net.proto2.python.internal import encoder
from google.net.proto2.python.internal import enum_type_wrapper
from google.net.proto2.python.internal import extension_dict
from google.net.proto2.python.internal import message_listener as message_listener_mod
from google.net.proto2.python.internal import type_checkers
from google.net.proto2.python.internal import well_known_types
from google.net.proto2.python.internal import wire_format
from google.net.proto2.python.public import descriptor as descriptor_mod
from google.net.proto2.python.public import message as message_mod
from google.net.proto2.python.public import text_format

_FieldDescriptor = descriptor_mod.FieldDescriptor
_AnyFullTypeName = 'google.protobuf.Any'
_ExtensionDict = extension_dict._ExtensionDict

class GeneratedProtocolMessageType(type):

  """Metaclass for protocol message classes created at runtime from Descriptors.

  We add implementations for all methods described in the Message class.  We
  also create properties to allow getting/setting all fields in the protocol
  message.  Finally, we create slots to prevent users from accidentally
  "setting" nonexistent fields in the protocol message, which then wouldn't get
  serialized / deserialized properly.

  The protocol compiler currently uses this metaclass to create protocol
  message classes at runtime.  Clients can also manually create their own
  classes at runtime, as in this example:

  mydescriptor = Descriptor(.....)
  factory = symbol_database.Default()
  factory.pool.AddDescriptor(mydescriptor)
  MyProtoClass = factory.GetPrototype(mydescriptor)
  myproto_instance = MyProtoClass()
  myproto.foo_field = 23
  ...
  """



  _DESCRIPTOR_KEY = 'DESCRIPTOR'

  def __new__(cls, name, bases, dictionary):
    """Custom allocation for runtime-generated class types.

    We override __new__ because this is apparently the only place
    where we can meaningfully set __slots__ on the class we're creating(?).
    (The interplay between metaclasses and slots is not very well-documented).

    Args:
      name: Name of the class (ignored, but required by the
        metaclass protocol).
      bases: Base classes of the class we're constructing.
        (Should be message.Message).  We ignore this field, but
        it's required by the metaclass protocol
      dictionary: The class dictionary of the class we're
        constructing.  dictionary[_DESCRIPTOR_KEY] must contain
        a Descriptor object describing this protocol message
        type.

    Returns:
      Newly-allocated class.
    """
    descriptor = dictionary[GeneratedProtocolMessageType._DESCRIPTOR_KEY]











    new_class = getattr(descriptor, '_concrete_class', None)
    if new_class:
      return new_class

    if descriptor.full_name in well_known_types.WKTBASES:
      bases += (well_known_types.WKTBASES[descriptor.full_name],)
    _AddClassAttributesForNestedExtensions(descriptor, dictionary)
    _AddSlots(descriptor, dictionary)

    superclass = super(GeneratedProtocolMessageType, cls)
    new_class = superclass.__new__(cls, name, bases, dictionary)
    return new_class

  def __init__(cls, name, bases, dictionary):
    """Here we perform the majority of our work on the class.
    We add enum getters, an __init__ method, implementations
    of all Message methods, and properties for all fields
    in the protocol type.

    Args:
      name: Name of the class (ignored, but required by the
        metaclass protocol).
      bases: Base classes of the class we're constructing.
        (Should be message.Message).  We ignore this field, but
        it's required by the metaclass protocol
      dictionary: The class dictionary of the class we're
        constructing.  dictionary[_DESCRIPTOR_KEY] must contain
        a Descriptor object describing this protocol message
        type.
    """
    descriptor = dictionary[GeneratedProtocolMessageType._DESCRIPTOR_KEY]



    existing_class = getattr(descriptor, '_concrete_class', None)
    if existing_class:
      assert existing_class is cls, (
          'Duplicate `GeneratedProtocolMessageType` created for descriptor %r'
          % (descriptor.full_name))
      return

    cls._decoders_by_tag = {}
    if (descriptor.has_options and
        descriptor.GetOptions().message_set_wire_format):
      cls._decoders_by_tag[decoder.MESSAGE_SET_ITEM_TAG] = (
          decoder.MessageSetItemDecoder(descriptor), None)


    for field in descriptor.fields:
      _AttachFieldHelpers(cls, field)

    descriptor._concrete_class = cls
    _AddEnumValues(descriptor, cls)
    _AddInitMethod(descriptor, cls)
    _AddPropertiesForFields(descriptor, cls)
    _AddPropertiesForExtensions(descriptor, cls)
    _AddStaticMethods(cls)
    _AddMessageMethods(descriptor, cls)
    _AddPrivateHelperMethods(descriptor, cls)

    superclass = super(GeneratedProtocolMessageType, cls)
    superclass.__init__(name, bases, dictionary)










def _PropertyName(proto_field_name):
  """Returns the name of the public property attribute which
  clients can use to get and (in some cases) set the value
  of a protocol message field.

  Args:
    proto_field_name: The protocol message field name, exactly
      as it appears (or would appear) in a .proto file.
  """

















  return proto_field_name


def _AddSlots(message_descriptor, dictionary):
  """Adds a __slots__ entry to dictionary, containing the names of all valid
  attributes for this message type.

  Args:
    message_descriptor: A Descriptor instance describing this message type.
    dictionary: Class dictionary to which we'll add a '__slots__' entry.
  """
  dictionary['__slots__'] = ['_cached_byte_size',
                             '_cached_byte_size_dirty',
                             '_fields',
                             '_unknown_fields',
                             '_unknown_field_set',
                             '_is_present_in_parent',
                             '_listener',
                             '_listener_for_children',
                             '__weakref__',
                             '_oneofs']


def _IsMessageSetExtension(field):
  return (field.is_extension and
          field.containing_type.has_options and
          field.containing_type.GetOptions().message_set_wire_format and
          field.type == _FieldDescriptor.TYPE_MESSAGE and
          field.label == _FieldDescriptor.LABEL_OPTIONAL)


def _IsMapField(field):
  return (field.type == _FieldDescriptor.TYPE_MESSAGE and
          field.message_type.has_options and
          field.message_type.GetOptions().map_entry)


def _IsMessageMapField(field):
  value_type = field.message_type.fields_by_name['value']
  return value_type.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE


def _IsStrictUtf8Check(field):
  if field.containing_type.syntax != 'proto3':
    return False
  enforce_utf8 = True

  enforce_utf8 = field.GetOptions().enforce_utf8

  return enforce_utf8


def _AttachFieldHelpers(cls, field_descriptor):
  is_repeated = (field_descriptor.label == _FieldDescriptor.LABEL_REPEATED)
  is_packable = (is_repeated and
                 wire_format.IsTypePackable(field_descriptor.type))
  if not is_packable:
    is_packed = False
  elif field_descriptor.containing_type.syntax == 'proto2':
    is_packed = (field_descriptor.has_options and
                field_descriptor.GetOptions().packed)
  else:
    has_packed_false = (field_descriptor.has_options and
                        field_descriptor.GetOptions().HasField('packed') and
                        field_descriptor.GetOptions().packed == False)
    is_packed = not has_packed_false
  is_map_entry = _IsMapField(field_descriptor)

  if is_map_entry:
    field_encoder = encoder.MapEncoder(field_descriptor)
    sizer = encoder.MapSizer(field_descriptor,
                             _IsMessageMapField(field_descriptor))
  elif _IsMessageSetExtension(field_descriptor):
    field_encoder = encoder.MessageSetItemEncoder(field_descriptor.number)
    sizer = encoder.MessageSetItemSizer(field_descriptor.number)
  else:
    field_encoder = type_checkers.TYPE_TO_ENCODER[field_descriptor.type](
        field_descriptor.number, is_repeated, is_packed)
    sizer = type_checkers.TYPE_TO_SIZER[field_descriptor.type](
        field_descriptor.number, is_repeated, is_packed)

  field_descriptor._encoder = field_encoder
  field_descriptor._sizer = sizer
  field_descriptor._default_constructor = _DefaultValueConstructorForField(
      field_descriptor)

  def AddDecoder(wiretype, is_packed):
    tag_bytes = encoder.TagBytes(field_descriptor.number, wiretype)
    decode_type = field_descriptor.type
    if (decode_type == _FieldDescriptor.TYPE_ENUM and
        type_checkers.SupportsOpenEnums(field_descriptor)):
      decode_type = _FieldDescriptor.TYPE_INT32

    oneof_descriptor = None
    if field_descriptor.containing_oneof is not None:
      oneof_descriptor = field_descriptor

    if is_map_entry:
      is_message_map = _IsMessageMapField(field_descriptor)

      field_decoder = decoder.MapDecoder(
          field_descriptor, _GetInitializeDefaultForMap(field_descriptor),
          is_message_map)
    elif decode_type == _FieldDescriptor.TYPE_STRING:
      is_strict_utf8_check = _IsStrictUtf8Check(field_descriptor)
      field_decoder = decoder.StringDecoder(
          field_descriptor.number, is_repeated, is_packed,
          field_descriptor, field_descriptor._default_constructor,
          is_strict_utf8_check)
    else:
      field_decoder = type_checkers.TYPE_TO_DECODER[decode_type](
          field_descriptor.number, is_repeated, is_packed,
          field_descriptor, field_descriptor._default_constructor)

    cls._decoders_by_tag[tag_bytes] = (field_decoder, oneof_descriptor)

  AddDecoder(type_checkers.FIELD_TYPE_TO_WIRE_TYPE[field_descriptor.type],
             False)

  if is_repeated and wire_format.IsTypePackable(field_descriptor.type):


    AddDecoder(wire_format.WIRETYPE_LENGTH_DELIMITED, True)


def _AddClassAttributesForNestedExtensions(descriptor, dictionary):
  extensions = descriptor.extensions_by_name
  for extension_name, extension_field in extensions.items():
    assert extension_name not in dictionary
    dictionary[extension_name] = extension_field


def _AddEnumValues(descriptor, cls):
  """Sets class-level attributes for all enum fields defined in this message.

  Also exporting a class-level object that can name enum values.

  Args:
    descriptor: Descriptor object for this message type.
    cls: Class we're constructing for this message type.
  """
  for enum_type in descriptor.enum_types:
    setattr(cls, enum_type.name, enum_type_wrapper.EnumTypeWrapper(enum_type))
    for enum_value in enum_type.values:
      setattr(cls, enum_value.name, enum_value.number)


def _GetInitializeDefaultForMap(field):
  if field.label != _FieldDescriptor.LABEL_REPEATED:
    raise ValueError('map_entry set on non-repeated field %s' % (
        field.name))
  fields_by_name = field.message_type.fields_by_name
  key_checker = type_checkers.GetTypeChecker(fields_by_name['key'])

  value_field = fields_by_name['value']
  if _IsMessageMapField(field):
    def MakeMessageMapDefault(message):
      return containers.MessageMap(
          message._listener_for_children, value_field.message_type, key_checker,
          field.message_type)
    return MakeMessageMapDefault
  else:
    value_checker = type_checkers.GetTypeChecker(value_field)
    def MakePrimitiveMapDefault(message):
      return containers.ScalarMap(
          message._listener_for_children, key_checker, value_checker,
          field.message_type)
    return MakePrimitiveMapDefault

def _DefaultValueConstructorForField(field):
  """Returns a function which returns a default value for a field.

  Args:
    field: FieldDescriptor object for this field.

  The returned function has one argument:
    message: Message instance containing this field, or a weakref proxy
      of same.

  That function in turn returns a default value for this field.  The default
    value may refer back to |message| via a weak reference.
  """

  if _IsMapField(field):
    return _GetInitializeDefaultForMap(field)

  if field.label == _FieldDescriptor.LABEL_REPEATED:
    if field.has_default_value and field.default_value != []:
      raise ValueError('Repeated field default value not empty list: %s' % (
          field.default_value))
    if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:


      message_type = field.message_type
      def MakeRepeatedMessageDefault(message):
        return containers.RepeatedCompositeFieldContainer(
            message._listener_for_children, field.message_type)
      return MakeRepeatedMessageDefault
    else:
      type_checker = type_checkers.GetTypeChecker(field)
      def MakeRepeatedScalarDefault(message):
        return containers.RepeatedScalarFieldContainer(
            message._listener_for_children, type_checker)
      return MakeRepeatedScalarDefault

  if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:

    message_type = field.message_type
    def MakeSubMessageDefault(message):
      assert getattr(message_type, '_concrete_class', None), (
          'Uninitialized concrete class found for field %r (message type %r)'
          % (field.full_name, message_type.full_name))
      result = message_type._concrete_class()
      result._SetListener(
          _OneofListener(message, field)
          if field.containing_oneof is not None
          else message._listener_for_children)
      return result
    return MakeSubMessageDefault

  def MakeScalarDefault(message):


    return field.default_value
  return MakeScalarDefault


def _ReraiseTypeErrorWithFieldName(message_name, field_name):
  """Re-raise the currently-handled TypeError with the field name added."""
  exc = sys.exc_info()[1]
  if len(exc.args) == 1 and type(exc) is TypeError:

    exc = TypeError('%s for field %s.%s' % (str(exc), message_name, field_name))


  six.reraise(type(exc), exc, sys.exc_info()[2])


def _AddInitMethod(message_descriptor, cls):
  """Adds an __init__ method to cls."""

  def _GetIntegerEnumValue(enum_type, value):
    """Convert a string or integer enum value to an integer.

    If the value is a string, it is converted to the enum value in
    enum_type with the same name.  If the value is not a string, it's
    returned as-is.  (No conversion or bounds-checking is done.)
    """
    if isinstance(value, six.string_types):
      try:
        return enum_type.values_by_name[value].number
      except KeyError:
        raise ValueError('Enum type %s: unknown label "%s"' % (
            enum_type.full_name, value))
    return value

  def init(self, **kwargs):
    self._cached_byte_size = 0
    self._cached_byte_size_dirty = len(kwargs) > 0
    self._fields = {}


    self._oneofs = {}



    self._unknown_fields = ()


    self._unknown_field_set = None
    self._is_present_in_parent = False
    self._listener = message_listener_mod.NullMessageListener()
    self._listener_for_children = _Listener(self)
    for field_name, field_value in kwargs.items():
      field = _GetFieldByName(message_descriptor, field_name)
      if field is None:
        raise TypeError('%s() got an unexpected keyword argument "%s"' %
                        (message_descriptor.name, field_name))
      if field_value is None:

        continue
      if field.label == _FieldDescriptor.LABEL_REPEATED:
        copy = field._default_constructor(self)
        if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
          if _IsMapField(field):
            if _IsMessageMapField(field):
              for key in field_value:
                copy[key].MergeFrom(field_value[key])
            else:
              copy.update(field_value)
          else:
            for val in field_value:
              if isinstance(val, dict):
                copy.add(**val)
              else:
                copy.add().MergeFrom(val)
        else:
          if field.cpp_type == _FieldDescriptor.CPPTYPE_ENUM:
            field_value = [_GetIntegerEnumValue(field.enum_type, val)
                           for val in field_value]
          copy.extend(field_value)
        self._fields[field] = copy
      elif field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
        copy = field._default_constructor(self)
        new_val = field_value
        if isinstance(field_value, dict):
          new_val = field.message_type._concrete_class(**field_value)
        try:
          copy.MergeFrom(new_val)
        except TypeError:
          _ReraiseTypeErrorWithFieldName(message_descriptor.name, field_name)
        self._fields[field] = copy
      else:
        if field.cpp_type == _FieldDescriptor.CPPTYPE_ENUM:
          field_value = _GetIntegerEnumValue(field.enum_type, field_value)
        try:
          setattr(self, field_name, field_value)
        except TypeError:
          _ReraiseTypeErrorWithFieldName(message_descriptor.name, field_name)

  init.__module__ = None
  init.__doc__ = None
  cls.__init__ = init


def _GetFieldByName(message_descriptor, field_name):
  """Returns a field descriptor by field name.

  Args:
    message_descriptor: A Descriptor describing all fields in message.
    field_name: The name of the field to retrieve.
  Returns:
    The field descriptor associated with the field name.
  """
  try:
    return message_descriptor.fields_by_name[field_name]
  except KeyError:
    raise ValueError('Protocol message %s has no "%s" field.' %
                     (message_descriptor.name, field_name))


def _AddPropertiesForFields(descriptor, cls):
  """Adds properties for all fields in this protocol message type."""
  for field in descriptor.fields:
    _AddPropertiesForField(field, cls)

  if descriptor.is_extendable:


    cls.Extensions = property(lambda self: _ExtensionDict(self))


def _AddPropertiesForField(field, cls):
  """Adds a public property for a protocol message field.
  Clients can use this property to get and (in the case
  of non-repeated scalar fields) directly set the value
  of a protocol message field.

  Args:
    field: A FieldDescriptor for this field.
    cls: The class we're constructing.
  """


  assert _FieldDescriptor.MAX_CPPTYPE == 10

  constant_name = field.name.upper() + '_FIELD_NUMBER'
  setattr(cls, constant_name, field.number)

  if field.label == _FieldDescriptor.LABEL_REPEATED:
    _AddPropertiesForRepeatedField(field, cls)
  elif field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
    _AddPropertiesForNonRepeatedCompositeField(field, cls)
  else:
    _AddPropertiesForNonRepeatedScalarField(field, cls)


class _FieldProperty(property):
  __slots__ = ('DESCRIPTOR',)

  def __init__(self, descriptor, getter, setter, doc):
    property.__init__(self, getter, setter, doc=doc)
    self.DESCRIPTOR = descriptor


def _AddPropertiesForRepeatedField(field, cls):
  """Adds a public property for a "repeated" protocol message field.  Clients
  can use this property to get the value of the field, which will be either a
  RepeatedScalarFieldContainer or RepeatedCompositeFieldContainer (see
  below).

  Note that when clients add values to these containers, we perform
  type-checking in the case of repeated scalar fields, and we also set any
  necessary "has" bits as a side-effect.

  Args:
    field: A FieldDescriptor for this field.
    cls: The class we're constructing.
  """
  proto_field_name = field.name
  property_name = _PropertyName(proto_field_name)

  def getter(self):
    field_value = self._fields.get(field)
    if field_value is None:

      field_value = field._default_constructor(self)







      field_value = self._fields.setdefault(field, field_value)
    return field_value
  getter.__module__ = None
  getter.__doc__ = 'Getter for %s.' % proto_field_name



  def setter(self, new_value):
    raise AttributeError('Assignment not allowed to repeated field '
                         '"%s" in protocol message object.' % proto_field_name)

  doc = 'Magic attribute generated for "%s" proto field.' % proto_field_name
  setattr(cls, property_name, _FieldProperty(field, getter, setter, doc=doc))


def _AddPropertiesForNonRepeatedScalarField(field, cls):
  """Adds a public property for a nonrepeated, scalar protocol message field.
  Clients can use this property to get and directly set the value of the field.
  Note that when the client sets the value of a field by using this property,
  all necessary "has" bits are set as a side-effect, and we also perform
  type-checking.

  Args:
    field: A FieldDescriptor for this field.
    cls: The class we're constructing.
  """
  proto_field_name = field.name
  property_name = _PropertyName(proto_field_name)
  type_checker = type_checkers.GetTypeChecker(field)
  default_value = field.default_value
  is_proto3 = field.containing_type.syntax == 'proto3'

  def getter(self):


    return self._fields.get(field, default_value)
  getter.__module__ = None
  getter.__doc__ = 'Getter for %s.' % proto_field_name

  clear_when_set_to_default = is_proto3 and not field.containing_oneof

  def field_setter(self, new_value):



    try:
      new_value = type_checker.CheckValue(new_value)
    except TypeError as e:
      raise TypeError(
          'Cannot set %s to %.1024r: %s' % (field.full_name, new_value, e))
    if clear_when_set_to_default and not new_value:
      self._fields.pop(field, None)
    else:
      self._fields[field] = new_value


    if not self._cached_byte_size_dirty:
      self._Modified()

  if field.containing_oneof:
    def setter(self, new_value):
      field_setter(self, new_value)
      self._UpdateOneofState(field)
  else:
    setter = field_setter

  setter.__module__ = None
  setter.__doc__ = 'Setter for %s.' % proto_field_name


  doc = 'Magic attribute generated for "%s" proto field.' % proto_field_name
  setattr(cls, property_name, _FieldProperty(field, getter, setter, doc=doc))


def _AddPropertiesForNonRepeatedCompositeField(field, cls):
  """Adds a public property for a nonrepeated, composite protocol message field.
  A composite field is a "group" or "message" field.

  Clients can use this property to get the value of the field, but cannot
  assign to the property directly.

  Args:
    field: A FieldDescriptor for this field.
    cls: The class we're constructing.
  """


  proto_field_name = field.name
  property_name = _PropertyName(proto_field_name)

  def getter(self):
    field_value = self._fields.get(field)
    if field_value is None:

      field_value = field._default_constructor(self)







      field_value = self._fields.setdefault(field, field_value)
    return field_value
  getter.__module__ = None
  getter.__doc__ = 'Getter for %s.' % proto_field_name



  def setter(self, new_value):
    raise AttributeError('Assignment not allowed to composite field '
                         '"%s" in protocol message object.' % proto_field_name)


  doc = 'Magic attribute generated for "%s" proto field.' % proto_field_name
  setattr(cls, property_name, _FieldProperty(field, getter, setter, doc=doc))


def _AddPropertiesForExtensions(descriptor, cls):
  """Adds properties for all fields in this protocol message type."""
  extensions = descriptor.extensions_by_name
  for extension_name, extension_field in extensions.items():
    constant_name = extension_name.upper() + '_FIELD_NUMBER'
    setattr(cls, constant_name, extension_field.number)



  if descriptor.file is not None:

    pool = descriptor.file.pool
    cls._extensions_by_number = pool._extensions_by_number[descriptor]
    cls._extensions_by_name = pool._extensions_by_name[descriptor]

def _AddStaticMethods(cls):

  def RegisterExtension(extension_handle):
    extension_handle.containing_type = cls.DESCRIPTOR


    cls.DESCRIPTOR.file.pool._AddExtensionDescriptor(extension_handle)
    _AttachFieldHelpers(cls, extension_handle)
  cls.RegisterExtension = staticmethod(RegisterExtension)

  def FromString(s):
    message = cls()
    message.MergeFromString(s)
    return message
  cls.FromString = staticmethod(FromString)


def _IsPresent(item):
  """Given a (FieldDescriptor, value) tuple from _fields, return true if the
  value should be included in the list returned by ListFields()."""

  if item[0].label == _FieldDescriptor.LABEL_REPEATED:
    return bool(item[1])
  elif item[0].cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
    return item[1]._is_present_in_parent
  else:
    return True


def _AddListFieldsMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""

  def ListFields(self):
    all_fields = [item for item in self._fields.items() if _IsPresent(item)]
    all_fields.sort(key = lambda item: item[0].number)
    return all_fields

  cls.ListFields = ListFields

_PROTO3_ERROR_TEMPLATE = 'Protocol message %s has no non-repeated submessage field "%s"'
_PROTO2_ERROR_TEMPLATE = 'Protocol message %s has no non-repeated field "%s"'

def _AddHasFieldMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""

  is_proto3 = (message_descriptor.syntax == "proto3")
  error_msg = _PROTO3_ERROR_TEMPLATE if is_proto3 else _PROTO2_ERROR_TEMPLATE

  hassable_fields = {}
  for field in message_descriptor.fields:
    if field.label == _FieldDescriptor.LABEL_REPEATED:
      continue

    if (is_proto3 and field.cpp_type != _FieldDescriptor.CPPTYPE_MESSAGE and
        not field.containing_oneof):
      continue
    hassable_fields[field.name] = field

  if not is_proto3:

    for oneof in message_descriptor.oneofs:
      hassable_fields[oneof.name] = oneof

  def HasField(self, field_name):
    try:
      field = hassable_fields[field_name]
    except KeyError:
      raise ValueError(error_msg % (message_descriptor.full_name, field_name))

    if isinstance(field, descriptor_mod.OneofDescriptor):
      try:
        return HasField(self, self._oneofs[field].name)
      except KeyError:
        return False
    else:
      if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
        value = self._fields.get(field)
        return value is not None and value._is_present_in_parent
      else:
        return field in self._fields

  cls.HasField = HasField


def _AddClearFieldMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""
  def ClearField(self, field_name):
    try:
      field = message_descriptor.fields_by_name[field_name]
    except KeyError:
      try:
        field = message_descriptor.oneofs_by_name[field_name]
        if field in self._oneofs:
          field = self._oneofs[field]
        else:
          return
      except KeyError:
        raise ValueError('Protocol message %s has no "%s" field.' %
                         (message_descriptor.name, field_name))

    if field in self._fields:


      if hasattr(self._fields[field], 'InvalidateIterators'):
        self._fields[field].InvalidateIterators()




      del self._fields[field]

      if self._oneofs.get(field.containing_oneof, None) is field:
        del self._oneofs[field.containing_oneof]




    self._Modified()

  cls.ClearField = ClearField


def _AddClearExtensionMethod(cls):
  """Helper for _AddMessageMethods()."""
  def ClearExtension(self, extension_handle):
    extension_dict._VerifyExtensionHandle(self, extension_handle)


    if extension_handle in self._fields:
      del self._fields[extension_handle]
    self._Modified()
  cls.ClearExtension = ClearExtension


def _AddHasExtensionMethod(cls):
  """Helper for _AddMessageMethods()."""
  def HasExtension(self, extension_handle):
    extension_dict._VerifyExtensionHandle(self, extension_handle)
    if extension_handle.label == _FieldDescriptor.LABEL_REPEATED:
      raise KeyError('"%s" is repeated.' % extension_handle.full_name)

    if extension_handle.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
      value = self._fields.get(extension_handle)
      return value is not None and value._is_present_in_parent
    else:
      return extension_handle in self._fields
  cls.HasExtension = HasExtension

def _InternalUnpackAny(msg):
  """Unpacks Any message and returns the unpacked message.

  This internal method is different from public Any Unpack method which takes
  the target message as argument. _InternalUnpackAny method does not have
  target message type and need to find the message type in descriptor pool.

  Args:
    msg: An Any message to be unpacked.

  Returns:
    The unpacked message.
  """




  from google.net.proto2.python.public import symbol_database
  factory = symbol_database.Default()

  type_url = msg.type_url

  if not type_url:
    return None



  type_name = type_url.split('/')[-1]
  descriptor = factory.pool.FindMessageTypeByName(type_name)

  if descriptor is None:
    return None

  message_class = factory.GetPrototype(descriptor)
  message = message_class()

  message.ParseFromString(msg.value)
  return message


def _AddEqualsMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""
  def __eq__(self, other):
    if (not isinstance(other, message_mod.Message) or
        other.DESCRIPTOR != self.DESCRIPTOR):
      return False

    if self is other:
      return True

    if self.DESCRIPTOR.full_name == _AnyFullTypeName:
      any_a = _InternalUnpackAny(self)
      any_b = _InternalUnpackAny(other)
      if any_a and any_b:
        return any_a == any_b

    if not self.ListFields() == other.ListFields():
      return False



    unknown_fields = list(self._unknown_fields)
    unknown_fields.sort()
    other_unknown_fields = list(other._unknown_fields)
    other_unknown_fields.sort()
    return unknown_fields == other_unknown_fields

  cls.__eq__ = __eq__


def _AddStrMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""
  def __str__(self):
    return text_format.MessageToString(self)
  cls.__str__ = __str__


def _AddReprMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""
  def __repr__(self):
    return text_format.MessageToString(self)
  cls.__repr__ = __repr__


def _AddUnicodeMethod(unused_message_descriptor, cls):
  """Helper for _AddMessageMethods()."""

  def __unicode__(self):
    return text_format.MessageToString(self, as_utf8=True).decode('utf-8')
  cls.__unicode__ = __unicode__


def _BytesForNonRepeatedElement(value, field_number, field_type):
  """Returns the number of bytes needed to serialize a non-repeated element.
  The returned byte count includes space for tag information and any
  other additional space associated with serializing value.

  Args:
    value: Value we're serializing.
    field_number: Field number of this value.  (Since the field number
      is stored as part of a varint-encoded tag, this has an impact
      on the total bytes required to serialize the value).
    field_type: The type of the field.  One of the TYPE_* constants
      within FieldDescriptor.
  """
  try:
    fn = type_checkers.TYPE_TO_BYTE_SIZE_FN[field_type]
    return fn(field_number, value)
  except KeyError:
    raise message_mod.EncodeError('Unrecognized field type: %d' % field_type)


def _AddByteSizeMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""

  def ByteSize(self):
    if not self._cached_byte_size_dirty:
      return self._cached_byte_size

    size = 0
    descriptor = self.DESCRIPTOR
    if descriptor.GetOptions().map_entry:

      size = descriptor.fields_by_name['key']._sizer(self.key)
      size += descriptor.fields_by_name['value']._sizer(self.value)
    else:
      for field_descriptor, field_value in self.ListFields():
        size += field_descriptor._sizer(field_value)
      for tag_bytes, value_bytes in self._unknown_fields:
        size += len(tag_bytes) + len(value_bytes)

    self._cached_byte_size = size
    self._cached_byte_size_dirty = False
    self._listener_for_children.dirty = False
    return size

  cls.ByteSize = ByteSize


def _AddSerializeToStringMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""

  def SerializeToString(self, **kwargs):

    if not self.IsInitialized():
      raise message_mod.EncodeError(
          'Message %s is missing required fields: %s' % (
          self.DESCRIPTOR.full_name, ','.join(self.FindInitializationErrors())))
    return self.SerializePartialToString(**kwargs)
  cls.SerializeToString = SerializeToString


def _AddSerializePartialToStringMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""

  def SerializePartialToString(self, **kwargs):
    out = BytesIO()
    self._InternalSerialize(out.write, **kwargs)
    return out.getvalue()
  cls.SerializePartialToString = SerializePartialToString

  def InternalSerialize(self, write_bytes, deterministic=None):
    if deterministic is None:
      deterministic = (
          api_implementation.IsPythonDefaultSerializationDeterministic())
    else:
      deterministic = bool(deterministic)

    descriptor = self.DESCRIPTOR
    if descriptor.GetOptions().map_entry:

      descriptor.fields_by_name['key']._encoder(
          write_bytes, self.key, deterministic)
      descriptor.fields_by_name['value']._encoder(
          write_bytes, self.value, deterministic)
    else:
      for field_descriptor, field_value in self.ListFields():
        field_descriptor._encoder(write_bytes, field_value, deterministic)
      for tag_bytes, value_bytes in self._unknown_fields:
        write_bytes(tag_bytes)
        write_bytes(value_bytes)
  cls._InternalSerialize = InternalSerialize


def _AddMergeFromStringMethod(message_descriptor, cls):
  """Helper for _AddMessageMethods()."""
  def MergeFromString(self, serialized):
    if isinstance(serialized, memoryview) and six.PY2:
      raise TypeError(
          'memoryview not supported in Python 2 with the pure Python proto '
          'implementation: this is to maintain compatibility with the C++ '
          'implementation')

    serialized = memoryview(serialized)
    length = len(serialized)
    try:
      if self._InternalParse(serialized, 0, length) != length:


        raise message_mod.DecodeError('Unexpected end-group tag.')
    except (IndexError, TypeError):

      raise message_mod.DecodeError('Truncated message.')
    except struct.error as e:
      raise message_mod.DecodeError(e)
    return length
  cls.MergeFromString = MergeFromString

  local_ReadTag = decoder.ReadTag
  local_SkipField = decoder.SkipField
  decoders_by_tag = cls._decoders_by_tag

  def InternalParse(self, buffer, pos, end):
    """Create a message from serialized bytes.

    Args:
      self: Message, instance of the proto message object.
      buffer: memoryview of the serialized data.
      pos: int, position to start in the serialized data.
      end: int, end position of the serialized data.

    Returns:
      Message object.
    """


    assert isinstance(buffer, memoryview)
    self._Modified()
    field_dict = self._fields

    unknown_field_set = self._unknown_field_set
    while pos != end:
      (tag_bytes, new_pos) = local_ReadTag(buffer, pos)
      field_decoder, field_desc = decoders_by_tag.get(tag_bytes, (None, None))
      if field_decoder is None:
        if not self._unknown_fields:
          self._unknown_fields = []
        if unknown_field_set is None:

          self._unknown_field_set = containers.UnknownFieldSet()

          unknown_field_set = self._unknown_field_set

        (tag, _) = decoder._DecodeVarint(tag_bytes, 0)
        field_number, wire_type = wire_format.UnpackTag(tag)
        if field_number == 0:
          raise message_mod.DecodeError('Field number 0 is illegal.')

        old_pos = new_pos
        (data, new_pos) = decoder._DecodeUnknownField(
            buffer, new_pos, wire_type)
        if new_pos == -1:
          return pos

        unknown_field_set._add(field_number, wire_type, data)

        new_pos = local_SkipField(buffer, old_pos, end, tag_bytes)
        if new_pos == -1:
          return pos
        self._unknown_fields.append(
            (tag_bytes, buffer[old_pos:new_pos].tobytes()))
        pos = new_pos
      else:
        pos = field_decoder(buffer, new_pos, end, self, field_dict)
        if field_desc:
          self._UpdateOneofState(field_desc)
    return pos
  cls._InternalParse = InternalParse


def _AddIsInitializedMethod(message_descriptor, cls):
  """Adds the IsInitialized and FindInitializationError methods to the
  protocol message class."""

  required_fields = [field for field in message_descriptor.fields
                           if field.label == _FieldDescriptor.LABEL_REQUIRED]

  def IsInitialized(self, errors=None):
    """Checks if all required fields of a message are set.

    Args:
      errors:  A list which, if provided, will be populated with the field
               paths of all missing required fields.

    Returns:
      True iff the specified message has all required fields set.
    """



    for field in required_fields:
      if (field not in self._fields or
          (field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE and
           not self._fields[field]._is_present_in_parent)):
        if errors is not None:
          errors.extend(self.FindInitializationErrors())
        return False

    for field, value in list(self._fields.items()):
      if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
        if field.label == _FieldDescriptor.LABEL_REPEATED:
          if (field.message_type.has_options and
              field.message_type.GetOptions().map_entry):
            continue
          for element in value:
            if not element.IsInitialized():
              if errors is not None:
                errors.extend(self.FindInitializationErrors())
              return False
        elif value._is_present_in_parent and not value.IsInitialized():
          if errors is not None:
            errors.extend(self.FindInitializationErrors())
          return False

    return True

  cls.IsInitialized = IsInitialized

  def FindInitializationErrors(self):
    """Finds required fields which are not initialized.

    Returns:
      A list of strings.  Each string is a path to an uninitialized field from
      the top-level message, e.g. "foo.bar[5].baz".
    """

    errors = []

    for field in required_fields:
      if not self.HasField(field.name):
        errors.append(field.name)

    for field, value in self.ListFields():
      if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
        if field.is_extension:
          name = '(%s)' % field.full_name
        else:
          name = field.name

        if _IsMapField(field):
          if _IsMessageMapField(field):
            for key in value:
              element = value[key]
              prefix = '%s[%s].' % (name, key)
              sub_errors = element.FindInitializationErrors()
              errors += [prefix + error for error in sub_errors]
          else:

            pass
        elif field.label == _FieldDescriptor.LABEL_REPEATED:
          for i in range(len(value)):
            element = value[i]
            prefix = '%s[%d].' % (name, i)
            sub_errors = element.FindInitializationErrors()
            errors += [prefix + error for error in sub_errors]
        else:
          prefix = name + '.'
          sub_errors = value.FindInitializationErrors()
          errors += [prefix + error for error in sub_errors]

    return errors

  cls.FindInitializationErrors = FindInitializationErrors


def _AddMergeFromMethod(cls):
  LABEL_REPEATED = _FieldDescriptor.LABEL_REPEATED
  CPPTYPE_MESSAGE = _FieldDescriptor.CPPTYPE_MESSAGE

  def MergeFrom(self, msg):
    if not isinstance(msg, cls):
      raise TypeError(
          'Parameter to MergeFrom() must be instance of same class: '
          'expected %s got %s.' % (cls.__name__, msg.__class__.__name__))

    assert msg is not self
    self._Modified()

    fields = self._fields

    for field, value in msg._fields.items():
      if field.label == LABEL_REPEATED:
        field_value = fields.get(field)
        if field_value is None:

          field_value = field._default_constructor(self)
          fields[field] = field_value
        field_value.MergeFrom(value)
      elif field.cpp_type == CPPTYPE_MESSAGE:
        if value._is_present_in_parent:
          field_value = fields.get(field)
          if field_value is None:

            field_value = field._default_constructor(self)
            fields[field] = field_value
          field_value.MergeFrom(value)
      else:
        self._fields[field] = value
        if field.containing_oneof:
          self._UpdateOneofState(field)

    if msg._unknown_fields:
      if not self._unknown_fields:
        self._unknown_fields = []
      self._unknown_fields.extend(msg._unknown_fields)

      if self._unknown_field_set is None:
        self._unknown_field_set = containers.UnknownFieldSet()
      self._unknown_field_set._extend(msg._unknown_field_set)

  cls.MergeFrom = MergeFrom


def _AddWhichOneofMethod(message_descriptor, cls):
  def WhichOneof(self, oneof_name):
    """Returns the name of the currently set field inside a oneof, or None."""
    try:
      field = message_descriptor.oneofs_by_name[oneof_name]
    except KeyError:
      raise ValueError(
          'Protocol message has no oneof "%s" field.' % oneof_name)

    nested_field = self._oneofs.get(field, None)
    if nested_field is not None and self.HasField(nested_field.name):
      return nested_field.name
    else:
      return None

  cls.WhichOneof = WhichOneof


def _Clear(self):

  self._fields = {}
  self._unknown_fields = ()

  if self._unknown_field_set is not None:
    self._unknown_field_set._clear()
    self._unknown_field_set = None

  self._oneofs = {}
  self._Modified()


def _UnknownFields(self):
  if self._unknown_field_set is None:

    self._unknown_field_set = containers.UnknownFieldSet()
  return self._unknown_field_set


def _DiscardUnknownFields(self):
  self._unknown_fields = []
  self._unknown_field_set = None
  for field, value in self.ListFields():
    if field.cpp_type == _FieldDescriptor.CPPTYPE_MESSAGE:
      if _IsMapField(field):
        if _IsMessageMapField(field):
          for key in value:
            value[key].DiscardUnknownFields()
      elif field.label == _FieldDescriptor.LABEL_REPEATED:
        for sub_message in value:
          sub_message.DiscardUnknownFields()
      else:
        value.DiscardUnknownFields()


def _SetListener(self, listener):
  if listener is None:
    self._listener = message_listener_mod.NullMessageListener()
  else:
    self._listener = listener


def _AddMessageMethods(message_descriptor, cls):
  """Adds implementations of all Message methods to cls."""
  _AddListFieldsMethod(message_descriptor, cls)
  _AddHasFieldMethod(message_descriptor, cls)
  _AddClearFieldMethod(message_descriptor, cls)
  if message_descriptor.is_extendable:
    _AddClearExtensionMethod(cls)
    _AddHasExtensionMethod(cls)
  _AddEqualsMethod(message_descriptor, cls)
  _AddStrMethod(message_descriptor, cls)
  _AddReprMethod(message_descriptor, cls)
  _AddUnicodeMethod(message_descriptor, cls)
  _AddByteSizeMethod(message_descriptor, cls)
  _AddSerializeToStringMethod(message_descriptor, cls)
  _AddSerializePartialToStringMethod(message_descriptor, cls)
  _AddMergeFromStringMethod(message_descriptor, cls)
  _AddIsInitializedMethod(message_descriptor, cls)
  _AddMergeFromMethod(cls)
  _AddWhichOneofMethod(message_descriptor, cls)

  cls.Clear = _Clear
  cls.UnknownFields = _UnknownFields
  cls.DiscardUnknownFields = _DiscardUnknownFields
  cls._SetListener = _SetListener


def _AddPrivateHelperMethods(message_descriptor, cls):
  """Adds implementation of private helper methods to cls."""

  def Modified(self):
    """Sets the _cached_byte_size_dirty bit to true,
    and propagates this to our listener iff this was a state change.
    """





    if not self._cached_byte_size_dirty:
      self._cached_byte_size_dirty = True
      self._listener_for_children.dirty = True
      self._is_present_in_parent = True
      self._listener.Modified()

  def _UpdateOneofState(self, field):
    """Sets field as the active field in its containing oneof.

    Will also delete currently active field in the oneof, if it is different
    from the argument. Does not mark the message as modified.
    """
    other_field = self._oneofs.setdefault(field.containing_oneof, field)
    if other_field is not field:
      del self._fields[other_field]
      self._oneofs[field.containing_oneof] = field

  cls._Modified = Modified
  cls.SetInParent = Modified
  cls._UpdateOneofState = _UpdateOneofState


class _Listener(object):

  """MessageListener implementation that a parent message registers with its
  child message.

  In order to support semantics like:

    foo.bar.baz.qux = 23
    assert foo.HasField('bar')

  ...child objects must have back references to their parents.
  This helper class is at the heart of this support.
  """

  def __init__(self, parent_message):
    """Args:
      parent_message: The message whose _Modified() method we should call when
        we receive Modified() messages.
    """




    if isinstance(parent_message, weakref.ProxyType):
      self._parent_message_weakref = parent_message
    else:
      self._parent_message_weakref = weakref.proxy(parent_message)




    self.dirty = False

  def Modified(self):
    if self.dirty:
      return
    try:

      self._parent_message_weakref._Modified()
    except ReferenceError:



      pass


class _OneofListener(_Listener):
  """Special listener implementation for setting composite oneof fields."""

  def __init__(self, parent_message, field):
    """Args:
      parent_message: The message whose _Modified() method we should call when
        we receive Modified() messages.
      field: The descriptor of the field being set in the parent message.
    """
    super(_OneofListener, self).__init__(parent_message)
    self._field = field

  def Modified(self):
    """Also updates the state of the containing oneof in the parent message."""
    try:
      self._parent_message_weakref._UpdateOneofState(self._field)
      super(_OneofListener, self).Modified()
    except ReferenceError:
      pass
