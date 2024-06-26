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


"""Utilities for generating and updating index.yaml."""

import logging
import os

import six
from six.moves import zip

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import validation
from google.appengine.api import yaml_errors
from google.appengine.datastore import datastore_index
from google.appengine.datastore import datastore_index_xml






__all__ = ['GenerateIndexFromHistory',
           'IndexYamlUpdater',
          ]

logger = logging.getLogger('google.appengine.api.stubs.datastore')


AUTO_MARKER = '\n# AUTOGENERATED\n'


AUTO_COMMENT = '''
# This index.yaml is automatically updated whenever the dev_appserver
# detects that a new type of query is run.  If you want to manage the
# index.yaml file manually, remove the above marker line (the line
# saying "# AUTOGENERATED").  If you want to manage some indexes
# manually, move them above the marker line.  The index.yaml file is
# automatically uploaded to the admin console when you next deploy
# your application using appcfg.py.
'''


def GenerateIndexDictFromHistory(query_history,
                                 all_indexes=None, manual_indexes=None):
  """Generate a dict of automatic index entries from the query history.

  Args:
    query_history: Query history, a dict mapping datastore_pb.Query to a count
      of the number of times that query has been issued.
    all_indexes: Optional datastore_index.IndexDefinitions instance
      representing all the indexes found in the input file.  May be None.
    manual_indexes: Optional datastore_index.IndexDefinitions instance
      containing indexes for which we should not generate output.  May be None.

  Returns:
    A dict where each key is a tuple (kind, ancestor, properties) and the
      corresponding value is a count of the number of times that query has been
      issued. The dict contains no entries for keys that appear in manual_keys.
      In the tuple, "properties" is itself a tuple of tuples, where each
      contained tuple is (name, direction), with "name" being a string and
      "direction" being datastore_index.ASCENDING or .DESCENDING.
  """



  all_keys = datastore_index.IndexDefinitionsToKeys(all_indexes)
  manual_keys = datastore_index.IndexDefinitionsToKeys(manual_indexes)


  indexes = dict((key, 0) for key in all_keys - manual_keys)


  for query, count in six.iteritems(query_history):
    required, kind, ancestor, props = (
        datastore_index.CompositeIndexForQuery(query))
    if required:
      props = datastore_index.GetRecommendedIndexProperties(props)
      spec = (kind, ancestor, props)




      if not any(_IndexSpecSatisfies(spec, k) for k in manual_keys):
        _UpdateGeneratedIndexes(spec, count, indexes)

  return indexes


def _UpdateGeneratedIndexes(spec, count, indexes):
  """Updates the set of generated indexes to cover given query requirements.

  It may add "spec" to the "indexes" dict if the latter does not
  already have an index suitable for serving the query represented by
  "spec".  (It may even replace an entry already in the dict if that
  gives optimal coverage.)

  Args:
    spec: specification of index requirements (in "key" form) for a
      query executed in the stub.
    count: number of times the query was executed
    indexes: dict containing other already-generated index "keys" and
      their counts.

  No return value; instead it Updates "indexes" in place as necessary.

  """




  for index in indexes:
    if _IndexSpecSatisfies(spec, index):
      indexes[index] += count
      return



  for index in indexes:
    if _IndexSpecSatisfies(index, spec):
      indexes[spec] = indexes[index] + count
      del indexes[index]
      return


  indexes[spec] = count


def _IndexSpecSatisfies(spec, candidate):
  """Determines whether candidate index can serve the query given by spec."""
  (spec_kind, spec_ancestor, spec_props) = spec
  (candidate_kind, candidate_ancestor, candidate_props) = candidate
  if (spec_kind, spec_ancestor) != (candidate_kind, candidate_ancestor):
    return False
  if len(spec_props) != len(candidate_props):
    return False
  return all(_PropSatisfies(s, c)
             for (s, c) in zip(spec_props, candidate_props))


def _PropSatisfies(spec, candidate):
  """Determines whether candidate property meets requirements given by spec."""


















  if spec.name != candidate.name or spec.mode != candidate.mode:
    return False

  return True if spec.direction is None else (
      spec.direction == candidate.direction)


def GenerateIndexFromHistory(query_history,
                             all_indexes=None, manual_indexes=None):
  """Generate most of the text for index.yaml from the query history.

  Args:
    query_history: Query history, a dict mapping datastore_pb.Query to a count
      of the number of times that query has been issued.
    all_indexes: Optional datastore_index.IndexDefinitions instance
      representing all the indexes found in the input file.  May be None.
    manual_indexes: Optional datastore_index.IndexDefinitions instance
      containing indexes for which we should not generate output.  May be None.

  Returns:
    A string representation that can safely be appended to an existing
    index.yaml file. Returns the empty string if it would generate no output.
  """
  indexes = GenerateIndexDictFromHistory(
      query_history, all_indexes, manual_indexes)

  if not indexes:
    return ''




  res = []
  for (kind, ancestor, props), _ in sorted(six.iteritems(indexes)):

    res.append('')
    res.append(datastore_index.IndexYamlForQuery(kind, ancestor, props))

  res.append('')
  return '\n'.join(res)


class EmptyIndexFileError(Exception):
  """Raised when index.yaml is empty."""


class IndexYamlUpdater(object):
  """Helper class for updating index.yaml.

  This class maintains some state about the query history and the
  index.yaml file in order to minimize the number of times index.yaml
  is actually overwritten.
  """


  index_yaml_is_manual = False
  index_yaml_mtime = None
  last_history_size = 0

  def __init__(self, root_path):
    """Constructor.

    Args:
      root_path: Path to the app's root directory.
    """
    self.root_path = root_path

  def UpdateIndexConfig(self):
    self.UpdateIndexYaml()

  def UpdateIndexYaml(self, openfile=open):
    """Update index.yaml.

    Args:
      openfile: Used for dependency injection.

    We only ever write to index.yaml if either:
    - it doesn't exist yet; or
    - it contains an 'AUTOGENERATED' comment.

    All indexes *before* the AUTOGENERATED comment will be written
    back unchanged.  All indexes *after* the AUTOGENERATED comment
    will be updated with the latest query counts (query counts are
    reset by --clear_datastore).  Indexes that aren't yet in the file
    will be appended to the AUTOGENERATED section.

    We keep track of some data in order to avoid doing repetitive work:
    - if index.yaml is fully manual, we keep track of its mtime to
      avoid parsing it over and over;
    - we keep track of the number of keys in the history dict since
      the last time we updated index.yaml (or decided there was
      nothing to update).
    """





    index_yaml_file = os.path.join(self.root_path, 'index.yaml')


    try:
      index_yaml_mtime = os.path.getmtime(index_yaml_file)
    except os.error:
      index_yaml_mtime = None


    index_yaml_changed = (index_yaml_mtime != self.index_yaml_mtime)
    self.index_yaml_mtime = index_yaml_mtime


    datastore_stub = apiproxy_stub_map.apiproxy.GetStub('datastore_v3')
    query_ci_history_len = datastore_stub._QueryCompositeIndexHistoryLength()
    history_changed = (query_ci_history_len != self.last_history_size)
    self.last_history_size = query_ci_history_len


    if not (index_yaml_changed or history_changed):
      logger.debug('No need to update index.yaml')
      return


    if self.index_yaml_is_manual and not index_yaml_changed:
      logger.debug('Will not update manual index.yaml')
      return


    if index_yaml_mtime is None:
      index_yaml_data = None
    else:
      try:



        fh = openfile(index_yaml_file, 'rU' if six.PY2 else 'r')
      except IOError:
        index_yaml_data = None
      else:
        try:
          index_yaml_data = fh.read()
          if not index_yaml_data:
            raise EmptyIndexFileError(
                'The index yaml file is empty. The file should at least have '
                'an empty "indexes:" block.')
        finally:
          fh.close()


    self.index_yaml_is_manual = (index_yaml_data is not None and
                                 AUTO_MARKER not in index_yaml_data)
    if self.index_yaml_is_manual:
      logger.info('Detected manual index.yaml, will not update')
      return



    if index_yaml_data is None:
      all_indexes = None
    else:
      try:
        all_indexes = datastore_index.ParseIndexDefinitions(index_yaml_data)
      except yaml_errors.EventListenerError as e:

        logger.error('Error parsing %s:\n%s', index_yaml_file, e)
        return
      except Exception as err:

        logger.error('Error parsing %s:\n%s.%s: %s', index_yaml_file,
                     err.__class__.__module__, err.__class__.__name__, err)
        return


    if index_yaml_data is None:
      manual_part, prev_automatic_part = 'indexes:\n', ''
      manual_indexes = None
    else:
      manual_part, prev_automatic_part = index_yaml_data.split(AUTO_MARKER, 1)
      if prev_automatic_part.startswith(AUTO_COMMENT):
        prev_automatic_part = prev_automatic_part[len(AUTO_COMMENT):]

      try:
        manual_indexes = datastore_index.ParseIndexDefinitions(manual_part)
      except Exception as err:
        logger.error('Error parsing manual part of %s: %s',
                     index_yaml_file, err)
        return


    automatic_part = GenerateIndexFromHistory(datastore_stub.QueryHistory(),
                                              all_indexes, manual_indexes)



    if (index_yaml_mtime is None and automatic_part == '' or
        automatic_part == prev_automatic_part):
      logger.debug('No need to update index.yaml')
      return


    try:
      fh = openfile(index_yaml_file, 'w')
    except IOError as err:
      logger.error('Can\'t write index.yaml: %s', err)
      return


    try:
      logger.info('Updating %s', index_yaml_file)
      fh.write(manual_part)
      fh.write(AUTO_MARKER)
      fh.write(AUTO_COMMENT)
      fh.write(automatic_part)
    finally:
      fh.close()


    try:
      self.index_yaml_mtime = os.path.getmtime(index_yaml_file)
    except os.error as err:
      logger.error('Can\'t stat index.yaml we just wrote: %s', err)
      self.index_yaml_mtime = None


class DatastoreIndexesAutoXmlUpdater(object):
  """Helper class for updating datastore-indexes-auto.xml.

  This class maintains some state about the query history and the
  datastore-indexes.xml and datastore-indexes-auto.xml files in order to
  minimize the number of times datastore-indexes-auto.xml is rewritten.
  """



  auto_generated = True
  datastore_indexes_xml = None
  datastore_indexes_xml_mtime = None
  datastore_indexes_auto_xml_mtime = None
  last_history_size = 0

  def __init__(self, root_path):
    self.root_path = root_path

  def UpdateIndexConfig(self):
    self.UpdateDatastoreIndexesAutoXml()

  def UpdateDatastoreIndexesAutoXml(self, openfile=open):
    """Update datastore-indexes-auto.xml if appropriate."""




    datastore_indexes_xml_file = os.path.join(
        self.root_path, 'WEB-INF', 'datastore-indexes.xml')
    try:
      datastore_indexes_xml_mtime = os.path.getmtime(datastore_indexes_xml_file)
    except os.error:
      datastore_indexes_xml_mtime = None
    if datastore_indexes_xml_mtime != self.datastore_indexes_xml_mtime:
      self.datastore_indexes_xml_mtime = datastore_indexes_xml_mtime
      if self.datastore_indexes_xml_mtime:
        with openfile(datastore_indexes_xml_file) as f:
          self.datastore_indexes_xml = f.read()
          self.auto_generated = datastore_index_xml.IsAutoGenerated(
              self.datastore_indexes_xml)
      else:
        self.auto_generated = True
        self.datastore_indexes_xml = None

    if not self.auto_generated:
      logger.debug('Detected <datastore-indexes autoGenerated="false">,'
                   ' will not update datastore-indexes-auto.xml')
      return


    datastore_stub = apiproxy_stub_map.apiproxy.GetStub('datastore_v3')
    query_ci_history_len = datastore_stub._QueryCompositeIndexHistoryLength()
    history_changed = (query_ci_history_len != self.last_history_size)
    self.last_history_size = query_ci_history_len
    if not history_changed:
      logger.debug('No need to update datastore-indexes-auto.xml')
      return

    datastore_indexes_auto_xml_file = os.path.join(
        self.root_path, 'WEB-INF', 'appengine-generated',
        'datastore-indexes-auto.xml')
    try:
      with open(datastore_indexes_auto_xml_file) as f:
        datastore_indexes_auto_xml = f.read()
    except IOError as err:
      datastore_indexes_auto_xml = None

    if self.datastore_indexes_xml:
      try:
        manual_index_definitions = (
            datastore_index_xml.IndexesXmlToIndexDefinitions(
                self.datastore_indexes_xml))
      except validation.ValidationError as e:
        logger.error('Error parsing %s: %s',
                     datastore_indexes_xml_file, e)
        return
    else:
      manual_index_definitions = datastore_index.IndexDefinitions(indexes=[])

    if datastore_indexes_auto_xml:
      try:
        prev_auto_index_definitions = (
            datastore_index_xml.IndexesXmlToIndexDefinitions(
                datastore_indexes_auto_xml))
      except validation.ValidationError as e:
        logger.error('Error parsing %s: %s',
                     datastore_indexes_auto_xml_file, e)
        return
    else:
      prev_auto_index_definitions = datastore_index.IndexDefinitions(indexes=[])

    all_index_definitions = datastore_index.IndexDefinitions(
        indexes=(manual_index_definitions.indexes +
                 prev_auto_index_definitions.indexes))
    query_history = datastore_stub.QueryHistory()
    auto_index_dict = GenerateIndexDictFromHistory(
        query_history, all_index_definitions, manual_index_definitions)
    auto_indexes, counts = self._IndexesFromIndexDict(auto_index_dict)
    auto_index_definitions = datastore_index.IndexDefinitions(
        indexes=auto_indexes)
    if auto_index_definitions == prev_auto_index_definitions:
      return

    try:
      appengine_generated = os.path.dirname(datastore_indexes_auto_xml_file)
      if not os.path.exists(appengine_generated):
        os.mkdir(appengine_generated)
      with open(datastore_indexes_auto_xml_file, 'w') as f:
        f.write(self._IndexXmlFromIndexes(auto_indexes, counts))
    except os.error as err:
      logger.error(
          'Could not update %s: %s', datastore_indexes_auto_xml_file, err)

  def _IndexesFromIndexDict(self, index_dict):
    """Convert a query dictionary into the corresponding required indexes.

    Args:
      index_dict: Index usage history, a dict mapping composite index
        descriptors to a count of the number of times that queries
        needing such an index have been executed

    Returns:
      a tuple (indexes, counts) where indexes and counts are lists of the same
      size, with each entry in indexes being a datastore_index.Index and each
      entry in indexes being the count of the number of times the corresponding
      query appeared in the history.
    """
    indexes = []
    counts = []
    for (kind, ancestor, props), count in sorted(six.iteritems(index_dict)):
      properties = []
      for prop in props:
        if prop.direction is None:
          direction = None
        else:
          direction = (
              'desc' if prop.direction == datastore_index.DESCENDING else 'asc')
        mode = (
            'geospatial' if prop.mode == datastore_index.GEOSPATIAL else None)
        properties.append(datastore_index.Property(
            name=prop.name, direction=direction, mode=mode))

      indexes.append(datastore_index.Index(
          kind=kind, ancestor=bool(ancestor), properties=properties))
      counts.append(count)

    return indexes, counts

  def _IndexXmlFromIndexes(self, indexes, counts):
    """Create <datastore-indexes> XML for the given indexes and query counts.

    Args:
      indexes: a list of datastore_index.Index objects that are the required
        indexes.
      counts: a list of integers that are the corresponding counts.

    Returns:
      the corresponding XML, with root node <datastore-indexes>.
    """
    lines = ['<datastore-indexes>']
    for index, count in zip(indexes, counts):
      lines.append('  <!-- Used %d time%s in query history -->'
                   % (count, 's' if count != 1 else ''))
      kind, ancestor, props = datastore_index.IndexToKey(index)
      xml_fragment = datastore_index.IndexXmlForQuery(kind, ancestor, props)
      lines.append(xml_fragment)

    lines.append('</datastore-indexes>')
    return '\n'.join(lines) + '\n'
