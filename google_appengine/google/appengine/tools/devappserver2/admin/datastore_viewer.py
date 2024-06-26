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
"""A handler that displays information about datastore entities."""

import datetime
import html
import math
import time

import google

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import metadata
from google.appengine._internal import six

from google.appengine.tools.devappserver2.admin import admin_request_handler


def _escape(s, quote=False):
  escaped = html.escape(s, quote=False)
  if quote:
    return escaped.replace('"', '&quot;')
  else:
    return escaped


def _format_datastore_key(key):
  """Return a nicely formatted decomposition of a datastore key.

  Args:
    key: The datastore_types.Key object to format.

  Returns:
    A string or Unicode object containing nicely formatted information about
    the given key e.g. "ParentKind: name=Animal > ChildKind: id=123".
  """
  path = key.to_path()  # [kind, id/name, kind, id/name, ...]
  parts = []
  for i in range(0, len(path)//2):
    kind = path[i*2]
    value = path[i*2 + 1]
    if isinstance(value, (int, long)):
      parts.append('%s: id=%d' % (kind, value))
    else:
      parts.append('%s: name=%s' % (kind, value))
  return ' > '.join(parts)


def _property_name_to_values(entities):
  """Returns a a mapping of entity property names to a list of their values.

  For example:
    _property_name_to_values([{'cat': 5, 'dog': 10},
                              {'dog': 15, 'mouse': 'happy'}])
    => {'cat': [5], 'dog': [10, 15], 'mouse': ['happy']}

  Args:
    entities: A sequence of mappings (i.e. datastore.Entity) that represent
        datastore properties and their values.

  Returns:
    A dict whose keys are the union of the keys of the given entities and
    whose values are the list of values for those keys.
  """
  property_name_to_values = {}
  for entity in entities:
    for property_name, value in entity.items():
      property_name_to_values.setdefault(property_name, []).append(value)

  return property_name_to_values


def _property_name_to_value(entities):
  """Returns a a mapping of entity property names to a sample value.

  For example:
    _property_name_to_value([{'cat': 5, 'dog': 10},
                             {'dog': 15, 'mouse': 'happy'}])
    => {'cat': 5, 'dog': 10 or 15, 'mouse': 'happy'}

  Args:
    entities: A sequence of mappings (i.e. datastore.Entity) that represent
        datastore properties and their values.

  Returns:
    A dict whose keys are the union of the keys of the given entities and
    whose values are arbitrarily chosen from the key values of the given
    entities.
  """
  return {key: values[0]
          for (key, values) in _property_name_to_values(entities).items()}


def _get_entities(kind, namespace, order, start, count):
  """Returns a list and a count of entities of the given kind.

  Args:
    kind: A string representing the name of the kind of the entities to
        return.
    namespace: A string representing the namespace of the entities to return.
    order: A string containing the name of the property to sorted the results
        by. A "-" prefix indicates descending order e.g. "-age".
    start: The number of initial entities to skip in the result set.
    count: The maximum number of entities to return.

  Returns:
    A tuple of (list of datastore.Entity, total entity count).
  """
  query = datastore.Query(kind, _namespace=namespace)

  if order:
    if order.startswith('-'):
      direction = datastore.Query.DESCENDING
      order = order[1:]
    else:
      direction = datastore.Query.ASCENDING
    query.Order((order, direction))

  total = query.Count()
  entities = query.Get(count, start)
  return entities, total


class DataType(object):
  """A DataType represents a data type in the datastore.

  Each DataType subtype defines four methods:

     format: returns a formatted string for a datastore value
     input_field: returns a string HTML <input> element for this DataType
     name: the friendly string name of this DataType
     parse: parses the formatted string representation of this DataType

  We use DataType instances to display formatted values in our result lists,
  and we uses input_field/format/parse to generate forms and parse the results
  from those forms to allow editing of entities.
  """

  _MAX_SHORT_LENGTH = 30
  # The value of the placeholder attribute generated by .input_field e.g.
  # <input ... placeholder="11-12-1974 12:12:53">.
  PLACEHOLDER = None

  @staticmethod
  def get(value):
    return _DATA_TYPES[value.__class__]

  @staticmethod
  def get_by_name(name):
    return _NAMED_DATA_TYPES[name]

  @classmethod
  def get_placholder_attribute(cls):
    if cls.PLACEHOLDER:
      return 'placeholder="%s"' % _escape(cls.PLACEHOLDER)
    else:
      return ''

  def format(self, value):
    if isinstance(value, six.string_types):
      return value
    else:
      return str(value)

  def short_format(self, value):
    format = self.format(value)
    if len(format) > self._MAX_SHORT_LENGTH:
      return format[:self._MAX_SHORT_LENGTH-3] + '...'
    else:
      return format

  def input_field(self, name, value, sample_values, back_uri):
    string_value = self.format(value) if value else ''
    return (
        '<input class="%s" name="%s" type="text" size="%d" value="%s" %s/>' % (
            _escape(self.name()),
            _escape(name),
            self.input_field_size(),
            _escape(string_value, True),
            self.get_placholder_attribute()))

  def input_field_size(self):
    return 30


class StringType(DataType):
  def input_field(self, name, value, sample_values, back_uri):
    string_value = self.format(value) if value else ''
    sample_values = [self.format(s) for s in sample_values]
    multiline = False
    if value:
      multiline = len(string_value) > 255 or string_value.find('\n') >= 0
    if not multiline:
      for sample_value in sample_values:
        if sample_value and (len(sample_value) > 255 or
                             sample_value.find('\n') >= 0):
          multiline = True
          break
    if multiline:
      return '<textarea name="%s" rows="5" cols="50" %s>%s</textarea>' % (
          _escape(name),
          self.get_placholder_attribute(),
          _escape(string_value))
    else:
      return DataType.input_field(self, name, value, sample_values, back_uri)

  def name(self):
    return 'string'

  def parse(self, value):
    return value

  def input_field_size(self):
    return 50


class TextType(StringType):
  def name(self):
    return 'Text'

  def input_field(self, name, value, sample_values, back_uri):
    string_value = self.format(value) if value else ''
    return '<textarea name="%s" rows="5" cols="50" %s>%s</textarea>' % (
        _escape(name),
        self.get_placholder_attribute(),
        _escape(string_value))

  def parse(self, value):
    return datastore_types.Text(value)


class ByteStringType(StringType):
  def format(self, value):
    # Format ByteString values as escaped Python strings.
    if value is None:
      return 'None'
    r = value.encode('string-escape')
    return r

  def name(self):
    return 'ByteString'

  def parse(self, value):
    # Parse escaped Python strings to ByteString values.
    # It is an error if the string contains non-ASCII values.
    bytestring = value.encode('ascii').decode('string-escape')
    return datastore_types.ByteString(bytestring)


class BlobType(StringType):
  def name(self):
    return 'Blob'

  def input_field(self, name, value, sample_values, back_uri):
    return '&lt;binary&gt;'

  def format(self, value):
    return '<binary>'


class EmbeddedEntityType(BlobType):
  def name(self):
    return 'entity:proto'


class TimeType(DataType):
  _FORMAT = '%Y-%m-%d %H:%M:%S'
  PLACEHOLDER = '2009-12-24 23:59:59'

  def format(self, value):
    return value.isoformat(' ')[0:19]

  def name(self):
    return 'datetime'

  def parse(self, value):
    return datetime.datetime(*(time.strptime(value,
                                             TimeType._FORMAT)[0:6]))


class OverflowTimeType(TimeType):
  def format(self, value):
    return str(value)

  def name(self):
    return 'overflowdatetime'

  def parse(self, value):
    try:
      return datastore_types._OverflowDateTime(value)
    except ValueError:
      return super(OverflowTimeType, self).parse(value)


class ListType(DataType):

  def name(self):
    return 'list'

  def input_field(self, name, value, sample_values, back_uri):
    string_value = self.format(value) if value else ''
    return _escape(string_value)


class BoolType(DataType):
  def name(self):
    return 'bool'

  def input_field(self, name, value, sample_values, back_uri):
    selected = {None: '', False: '', True: ''}
    selected[value] = 'selected'
    return """<select class="%s" name="%s">
    <option %s value=''></option>
    <option %s value='0'>False</option>
    <option %s value='1'>True</option></select>""" % (
        _escape(self.name()), _escape(name), selected[None],
        selected[False], selected[True])

  def parse(self, value):
    if value.lower() == 'true':
      return True
    if value.lower() == 'false':
      return False
    # Otherwise treat as an int
    return bool(int(value))


class NumberType(DataType):

  def input_field(self, name, value, sample_values, back_uri):
    string_value = self.format(value) if value is not None else ''
    return super(NumberType, self).input_field(name,
                                               string_value,
                                               sample_values,
                                               back_uri)


class IntType(NumberType):
  PLACEHOLDER = '42'

  def input_field_size(self):
    return 10

  def name(self):
    return 'int'

  def parse(self, value):
    return int(value)


class FloatType(NumberType):
  PLACEHOLDER = '3.14159'

  def name(self):
    return 'float'

  def parse(self, value):
    return float(value)


class UserType(DataType):
  PLACEHOLDER = 'john@example.com'

  def name(self):
    return 'User'

  def parse(self, value):
    return users.User(value)

  def input_field_size(self):
    return 15


_ESCAPE_FUNC = html.escape


# This is incomplete, but enough to make the system still work.
class ReferenceType(DataType):
  def name(self):
    return 'Key'

  def short_format(self, value):
    return str(value)[:8] + '...'

  def parse(self, value):
    return datastore_types.Key(value)

  def input_field(self, name, value, sample_values, back_uri):
    # pylint: disable=deprecated-method
    string_value = self.format(value) if value else ''
    html_text = '<input class="%s" name="%s" type="text" size="%d" value="%s"/>' % (
        _ESCAPE_FUNC(self.name()), _ESCAPE_FUNC(name), self.input_field_size(),
        _ESCAPE_FUNC(string_value))
    if value:
      html_text += '<br><a href="/datastore/edit/%s?next=%s">%s</a>' % (
          _ESCAPE_FUNC(string_value),
          six.moves.urllib.parse.quote_plus(back_uri),
          _ESCAPE_FUNC(_format_datastore_key(value), True))
    return html_text

  def input_field_size(self):
    return 85


class EmailType(StringType):
  PLACEHOLDER = 'john@example.com'

  def name(self):
    return 'Email'

  def parse(self, value):
    return datastore_types.Email(value)


class CategoryType(StringType):
  def name(self):
    return 'Category'

  def parse(self, value):
    return datastore_types.Category(value)


class LinkType(StringType):
  PLACEHOLDER = 'http://www.example.com/'

  def name(self):
    return 'Link'

  def parse(self, value):
    return datastore_types.Link(value)


class GeoPtType(DataType):
  PLACEHOLDER = '33.86,-151.2'

  def name(self):
    return 'GeoPt'

  def parse(self, value):
    return datastore_types.GeoPt(value)


class ImType(DataType):
  PLACEHOLDER = 'xmpp john@example.com'

  def name(self):
    return 'IM'

  def parse(self, value):
    return datastore_types.IM(value)


class PhoneNumberType(StringType):
  def name(self):
    return 'PhoneNumber'

  def parse(self, value):
    return datastore_types.PhoneNumber(value)


class PostalAddressType(StringType):
  def name(self):
    return 'PostalAddress'

  def parse(self, value):
    return datastore_types.PostalAddress(value)


class RatingType(DataType):
  PLACEHOLDER = '93'

  def input_field_size(self):
    return 5

  def name(self):
    return 'Rating'

  def parse(self, value):
    return datastore_types.Rating(value)


class NoneType(DataType):
  def name(self):
    return 'None'

  def parse(self, value):
    return None

  def format(self, value):
    return 'None'


class BlobKeyType(StringType):
  def name(self):
    return 'BlobKey'

  def parse(self, value):
    return datastore_types.BlobKey(value)


# Maps Pyathon/datatstore types to DataType instances
_DATA_TYPES = {
    type(None): NoneType(),
    bytes: StringType(),
    str: StringType(),
    datastore_types.Text: TextType(),
    datastore_types.Blob: BlobType(),
    datastore_types.EmbeddedEntity: EmbeddedEntityType(),
    bool: BoolType(),
    int: IntType(),
    int: IntType(),
    float: FloatType(),
    datetime.datetime: TimeType(),
    datastore_types._OverflowDateTime: OverflowTimeType(),
    users.User: UserType(),
    datastore_types.Key: ReferenceType(),
    list: ListType(),
    datastore_types.Email: EmailType(),
    datastore_types.Category: CategoryType(),
    datastore_types.Link: LinkType(),
    datastore_types.GeoPt: GeoPtType(),
    datastore_types.IM: ImType(),
    datastore_types.PhoneNumber: PhoneNumberType(),
    datastore_types.PostalAddress: PostalAddressType(),
    datastore_types.Rating: RatingType(),
    datastore_types.BlobKey: BlobKeyType(),
    datastore_types.ByteString: ByteStringType(),
}

_NAMED_DATA_TYPES = {}
for _data_type in _DATA_TYPES.values():
  _NAMED_DATA_TYPES[_data_type.name()] = _data_type


class DatastoreRequestHandler(admin_request_handler.AdminRequestHandler):
  """A handler that displays information about datastore entities."""

  NUM_ENTITIES_PER_PAGE = 20

  @staticmethod
  def _calculate_writes_for_built_in_indices(entity):
    writes = 0
    for prop_name in entity.keys():
      if not prop_name in entity.unindexed_properties():
        # 2 writes per property value, one for EntitiesByProperty and one for
        # EntitiesbyPropertyDesc
        prop_vals = entity[prop_name]
        if isinstance(prop_vals, (list)):
          num_prop_vals = len(prop_vals)
        else:
          num_prop_vals = 1
        writes += 2 * num_prop_vals
    return writes

  @staticmethod
  def _get_kinds(namespace):
    """Return a sorted list of kind names present in the given namespace."""
    assert namespace is not None
    q = metadata.Kind.all(namespace=namespace)
    return sorted([x.kind_name for x in q.run()])

  @classmethod
  def _get_entity_template_data(cls,
                                request_uri,
                                kind,
                                namespace,
                                order,
                                start):

    entities, total_entities = _get_entities(kind,
                                             namespace,
                                             order,
                                             start,
                                             cls.NUM_ENTITIES_PER_PAGE)

    property_name_to_value = _property_name_to_value(entities)

    headers = [{'name': property_name}
               for property_name in sorted(property_name_to_value)]

    template_entities = []
    for entity in entities:
      attributes = []
      for property_name in sorted(property_name_to_value):
        if property_name in entity:
          raw_value = entity[property_name]
          data_type = DataType.get(raw_value)
          value = data_type.format(raw_value)
          short_value = data_type.short_format(raw_value)
        else:
          value = ''
          short_value = ''
        attributes.append({'name': property_name,
                           'value': value,
                           'short_value': short_value,
                          })
      edit_uri = '/datastore/edit/%s?next=%s' % (
          entity.key(), six.moves.urllib.parse.quote(request_uri))
      template_entities.append(
          {'attributes': attributes,
           'edit_uri': edit_uri,
           'key': entity.key(),
           'key_id': entity.key().id(),
           'key_name': entity.key().name(),
           'shortened_key': str(entity.key())[:8] + '...'})
    return headers, template_entities, total_entities

  def get(self):
    super(DatastoreRequestHandler, self).get()
    # Force all transactions to complete to show the user consistent results.
    datastore_stub = apiproxy_stub_map.apiproxy.GetStub('datastore_v3')
    datastore_stub.Flush()

    kind = self.request.get('kind', None)
    namespace = self.request.get('namespace', '')
    order = self.request.get('order', None)
    message = self.request.get('message', None)

    try:
      page = int(self.request.get('page', '1'))
    except ValueError:
      page = 1

    kinds = self._get_kinds(namespace)
    if not kind and kinds:
      self.redirect(self._construct_url(add={'kind': kinds[0]}))
      return

    if kind:
      start = (page-1) * self.NUM_ENTITIES_PER_PAGE
      headers, template_entities, total_entities = (
          self._get_entity_template_data(
              self.request.uri,
              kind,
              namespace,
              order,
              start))
      num_pages = int(math.ceil(float(total_entities) /
                                self.NUM_ENTITIES_PER_PAGE))
    else:
      start = 0
      headers = []
      template_entities = []
      total_entities = 0
      num_pages = 0

    select_namespace_url = self._construct_url(
        remove=['message'],
        add={'namespace': self.request.get('namespace')})
    self.response.write(self.render(
        'datastore_viewer.html',
        {'entities': template_entities,
         'headers': headers,
         'kind': kind,
         'kinds': kinds,
         'message': message,
         'namespace': namespace,
         'num_pages': num_pages,
         'order': order,
         'order_base_url': self._construct_url(remove=['message', 'order']),
         'page': page,
         'paging_base_url': self._construct_url(remove=['message', 'page']),
         'select_namespace_url': select_namespace_url,
         'show_namespace': self.request.get('namespace', None) is not None,
         'start': start,
         'total_entities': total_entities}))

  def post(self):
    """Handle modifying actions and redirect to a GET page."""
    super(DatastoreRequestHandler, self).post()
    if self.request.get('action:flush_memcache'):
      if memcache.flush_all():
        message = 'Cache flushed, all keys dropped.'
      else:
        message = 'Flushing the cache failed. Please try again.'
      self.redirect(self._construct_url(remove=['action:flush_memcache'],
                                        add={'message': message}))
    elif self.request.get('action:delete_entities'):
      entity_keys = self.request.params.getall('entity_key')
      db.delete(entity_keys)
      self.redirect(self._construct_url(
          remove=['action:delete_entities'],
          add={'message': '%d entities deleted' % len(entity_keys)}))
    else:
      self.error(404)


class DatastoreEditRequestHandler(admin_request_handler.AdminRequestHandler):
  """A handler that allows datastore entities to be created and edited."""

  def get(self, entity_key_string=None):
    super(DatastoreEditRequestHandler, self).get(entity_key_string)
    if entity_key_string:
      entity_key = datastore.Key(entity_key_string)
      entity_key_name = entity_key.name()
      entity_key_id = entity_key.id()
      namespace = entity_key.namespace()
      kind = entity_key.kind()
      entities = [datastore.Get(entity_key)]
      parent_key = entity_key.parent()
      if parent_key:
        parent_key_string = _format_datastore_key(parent_key)
      else:
        parent_key_string = None
    else:
      entity_key = None
      entity_key_string = None
      entity_key_name = None
      entity_key_id = None
      namespace = self.request.get('namespace')
      kind = self.request.get('kind')
      entities, _ = _get_entities(kind,
                                  namespace,
                                  order=None,
                                  start=0,
                                  count=20)
      parent_key = None
      parent_key_string = None

      if not entities:
        self.redirect('/datastore?%s' % (six.moves.urllib.parse.urlencode(
            [('kind', kind),
             ('message',
              'Cannot create the kind "%s" in the "%s" namespace because '
              'no template entity exists.' % (kind, namespace)),
             ('namespace', namespace)])))
        return

    property_name_to_values = _property_name_to_values(entities)
    fields = []
    for property_name, values in sorted(property_name_to_values.items()):
      data_type = DataType.get(values[0])
      field = data_type.input_field('%s|%s' % (data_type.name(), property_name),
                                    values[0] if entity_key else None,
                                    values,
                                    self.request.uri)
      fields.append((property_name, data_type.name(), field))

    self.response.write(self.render(
        'datastore_edit.html',
        {'fields': fields,
         'key': entity_key_string,
         'key_id': entity_key_id,
         'key_name': entity_key_name,
         'kind': kind,
         'namespace': namespace,
         'next': self.request.get('next', '/datastore'),
         'parent_key': parent_key,
         'parent_key_string': parent_key_string}))

  def post(self, entity_key_string=None):
    super(DatastoreEditRequestHandler, self).post(entity_key_string)
    if self.request.get('action:delete'):
      if entity_key_string:
        datastore.Delete(datastore.Key(entity_key_string))
        self.redirect(str(self.request.get('next', '/datastore')))
      else:
        self.response.set_status(400)
      return

    if entity_key_string:
      entity = datastore.Get(datastore.Key(entity_key_string))
    else:
      kind = self.request.get('kind')
      namespace = self.request.get('namespace', None)
      entity = datastore.Entity(kind, _namespace=namespace)

    for arg_name in self.request.arguments():
      # Arguments are in <property_type>|<property_name>=<value> format.
      if '|' not in arg_name:
        continue
      data_type_name, property_name = arg_name.split('|')
      form_value = self.request.get(arg_name)
      data_type = DataType.get_by_name(data_type_name)
      if (entity and
          property_name in entity and
          data_type.format(entity[property_name]) == form_value):
        # If the property is unchanged then don't update it. This will prevent
        # empty form values from causing the property to be deleted if the
        # property was already empty.
        continue

      if form_value:
        # TODO: Handle parse exceptions.
        entity[property_name] = data_type.parse(form_value)
      elif property_name in entity:
        # TODO: Treating empty input as deletion is a not a good
        # interface.
        del entity[property_name]

    datastore.Put(entity)
    self.redirect(str(self.request.get('next', '/datastore')))
