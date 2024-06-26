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
"""Stub implementation for Log Service that uses sqlite."""

import atexit
import codecs
import datetime
import logging
import time

import sqlite3

from google.appengine.api import apiproxy_stub
from google.appengine.api import appinfo
from google.appengine.api.logservice import log_service_pb2
from google.appengine.runtime import apiproxy_errors


_REQUEST_LOG_CREATE = """
CREATE TABLE IF NOT EXISTS RequestLogs (
  id INTEGER NOT NULL PRIMARY KEY,
  user_request_id TEXT NOT NULL,
  app_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  module TEXT NOT NULL,
  ip TEXT NOT NULL,
  nickname TEXT NOT NULL,
  start_time INTEGER NOT NULL,
  end_time INTEGER DEFAULT 0 NOT NULL,
  method TEXT NOT NULL,
  resource TEXT NOT NULL,
  http_version TEXT NOT NULL,
  status INTEGER DEFAULT 0 NOT NULL,
  response_size INTEGER DEFAULT 0 NOT NULL,
  user_agent TEXT NOT NULL,
  url_map_entry TEXT DEFAULT '' NOT NULL,
  host TEXT NOT NULL,
  referrer TEXT,
  task_queue_name TEXT DEFAULT '' NOT NULL,
  task_name TEXT DEFAULT '' NOT NULL,
  latency INTEGER DEFAULT 0 NOT NULL,
  mcycles INTEGER DEFAULT 0 NOT NULL,
  finished INTEGER DEFAULT 0 NOT NULL
);
"""

_REQUEST_LOG_ADD_MODULE_COLUMN = """
ALTER TABLE RequestLogs
  ADD COLUMN module TEXT DEFAULT '%s' NOT NULL;
""" % appinfo.DEFAULT_MODULE

_APP_LOG_CREATE = """
CREATE TABLE IF NOT EXISTS AppLogs (
  id INTEGER NOT NULL PRIMARY KEY,
  request_id INTEGER NOT NULL,
  timestamp INTEGER NOT NULL,
  level INTEGER NOT NULL,
  message TEXT NOT NULL,
  FOREIGN KEY(request_id) REFERENCES RequestLogs(id)
);
"""


class LogServiceStub(apiproxy_stub.APIProxyStub):
  """Python stub for Log Service service."""

  THREADSAFE = True

  _ACCEPTS_REQUEST_ID = True


  _DEFAULT_READ_COUNT = 20


  _MIN_COMMIT_INTERVAL = 5

  def __init__(self, persist=False, logs_path=None, request_data=None):
    """Initializer.

    Args:
      persist: For backwards compatability. Has no effect.
      logs_path: A str containing the filename to use for logs storage. Defaults
        to in-memory if unset.
      request_data: A apiproxy_stub.RequestData instance used to look up state
        associated with the request that generated an API call.
    """

    super(LogServiceStub, self).__init__('logservice',
                                         request_data=request_data)
    self._logs_path = logs_path or ':memory:'
    self._init_sqlite3_conn()
    atexit.register(self._conn.commit)

  @apiproxy_stub.Synchronized
  def _init_sqlite3_conn(self):
    """Initializes a SQLite3 connection for the LogServiceStub.

    Initializes a connection, creates relevant tables, and sets associated
    instance variables.
    """
    self._request_id_to_request_row_id = {}
    self._conn = sqlite3.connect(self._logs_path, check_same_thread=False)
    self._conn.row_factory = sqlite3.Row
    self._conn.execute(_REQUEST_LOG_CREATE)
    self._conn.execute(_APP_LOG_CREATE)

    column_names = set(c['name'] for c in
                       self._conn.execute('PRAGMA table_info(RequestLogs)'))
    if 'module' not in column_names:
      self._conn.execute(_REQUEST_LOG_ADD_MODULE_COLUMN)
    self._last_commit = time.time()

  @staticmethod
  def _get_time_usec():
    return int(time.time() * 1e6)

  def _maybe_commit(self):
    now = time.time()
    if (now - self._last_commit) > self._MIN_COMMIT_INTERVAL:
      self._conn.commit()
      self._last_commit = now

  @apiproxy_stub.Synchronized
  def start_request(self, request_id, user_request_id, ip, app_id, version_id,
                    nickname, user_agent, host, method, resource, http_version,
                    start_time=None, module=None):
    """Starts logging for a request.

    Each start_request call must be followed by a corresponding end_request call
    to cleanup resources allocated in start_request.

    Args:
      request_id: A unique string identifying the request associated with the
        API call.
      user_request_id: A user-visible unique string for retrieving the request
        log at a later time.
      ip: The user's IP address.
      app_id: A string representing the application ID that this request
        corresponds to.
      version_id: A string representing the version ID that this request
        corresponds to.
      nickname: A string representing the user that has made this request (that
        is, the user's nickname, e.g., 'foobar' for a user logged in as
        'foobar@gmail.com').
      user_agent: A string representing the agent used to make this request.
      host: A string representing the host that received this request.
      method: A string containing the HTTP method of this request.
      resource: A string containing the path and query string of this request.
      http_version: A string containing the HTTP version of this request.
      start_time: An int containing the start time in micro-seconds. If unset,
        the current time is used.
      module: The string name of the module handling this request.
    """
    if module is None:
      module = appinfo.DEFAULT_MODULE
    if version_id is None:
      version_id = 'NO-VERSION'
    major_version_id = version_id.split('.', 1)[0]
    if start_time is None:
      start_time = self._get_time_usec()
    cursor = self._conn.execute(
        'INSERT INTO RequestLogs (user_request_id, ip, app_id, version_id, '
        'nickname, user_agent, host, start_time, method, resource, '
        'http_version, module)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
            user_request_id, ip, app_id, major_version_id, nickname, user_agent,
            host, start_time, method, resource, http_version, module))
    self._request_id_to_request_row_id[request_id] = cursor.lastrowid
    self._maybe_commit()

  @apiproxy_stub.Synchronized
  def end_request(self, request_id, status, response_size, end_time=None):
    """Ends logging for a request.

    Args:
      request_id: A unique string identifying the request associated with the
        API call.
      status: An int containing the HTTP status code for this request.
      response_size: An int containing the content length of the response.
      end_time: An int containing the end time in micro-seconds. If unset, the
        current time is used.
    """
    row_id = self._request_id_to_request_row_id.pop(request_id, None)
    if not row_id:
      return
    if end_time is None:
      end_time = self._get_time_usec()
    self._conn.execute(
        'UPDATE RequestLogs SET '
        'status = ?, response_size = ?, end_time = ?, finished = 1 '
        'WHERE id = ?', (
            status, response_size, end_time, row_id))
    self._maybe_commit()

  def _Dynamic_Flush(self, request, unused_response, request_id):
    """Writes application-level log messages for a request."""
    group = log_service_pb2.UserAppLogGroup().FromString(request.logs)
    self._insert_app_logs(request_id, group.log_line)

  @apiproxy_stub.Synchronized
  def _insert_app_logs(self, request_id, log_lines):
    row_id = self._request_id_to_request_row_id.get(request_id)
    if row_id is None:
      return
    new_app_logs = (self._tuple_from_log_line(row_id, log_line)
                    for log_line in log_lines)
    self._conn.executemany(
        'INSERT INTO AppLogs (request_id, timestamp, level, message) VALUES '
        '(?, ?, ?, ?)', new_app_logs)
    self._maybe_commit()

  @staticmethod
  def _tuple_from_log_line(request_id, log_line):
    """Returns a tuple of (request_id, timestamp, level, message).

    Used to generate a tuple for a SQLite3 paramaterized query.

    Args:
      request_id: The string request ID.
      log_line: An instance of log_service_pb2.LogLine or
        log_service_pb2.UserAppLogLine.

    Returns:
      A tuple of (request_id, timestamp, level, message).
    """
    if isinstance(log_line, log_service_pb2.UserAppLogLine):
      message = log_line.message
      timestamp = log_line.timestamp_usec
    elif isinstance(log_line, log_service_pb2.LogLine):
      message = log_line.log_message
      timestamp = log_line.time
    else:
      raise TypeError(
          'Expected an instance of log_service_pb2.LogLine or '
          'log_service_pb2.UserAppLogLine. Received an instance of %s.' %
          type(log_line))
    if isinstance(message, bytes):
      message = codecs.decode(message, 'utf-8', 'replace')
    return (request_id, timestamp, log_line.level, message)

  @apiproxy_stub.Synchronized
  def _Dynamic_Read(self, request, response, request_id):
    if (len(request.module_version) < 1 and
        len(request.version_id_size) < 1 and
        len(request.request_id) < 1):
      raise apiproxy_errors.ApplicationError(
          log_service_pb2.LogServiceError.INVALID_REQUEST)

    if len(request.module_version) > 0 and len(request.version_id) > 0:
      raise apiproxy_errors.ApplicationError(
          log_service_pb2.LogServiceError.INVALID_REQUEST)

    if (len(request.request_id) and
        (request.HasField('start_time') or request.HasField('end_time') or
         request.HasField('offset'))):
      raise apiproxy_errors.ApplicationError(
          log_service_pb2.LogServiceError.INVALID_REQUEST)

    if len(request.request_id):
      for request_id in request.request_id:
        log_row = self._conn.execute(
            'SELECT * FROM RequestLogs WHERE user_request_id = ?',
            (request_id.decode('utf-8'),)).fetchone()
        if log_row:
          log = response.log.add()
          self._fill_request_log(log_row, log, request.include_app_logs)
      return

    if request.HasField('count'):
      count = request.count
    else:
      count = self._DEFAULT_READ_COUNT
    filters, values = self._extract_read_filters(request)
    filter_string = ' WHERE %s' % ' and '.join(filters)

    if request.HasField('minimum_log_level'):
      query = ('SELECT * FROM RequestLogs INNER JOIN AppLogs ON '
               'RequestLogs.id = AppLogs.request_id%s GROUP BY '
               'RequestLogs.id ORDER BY id DESC')
    else:
      query = 'SELECT * FROM RequestLogs%s ORDER BY id DESC'
    logs = self._conn.execute(query % filter_string,
                              values).fetchmany(count + 1)
    if logging.getLogger(__name__).isEnabledFor(logging.DEBUG):
      self._debug_query(filter_string, values, len(logs))
    for log_row in logs[:count]:
      log = response.log.add()
      self._fill_request_log(log_row, log, request.include_app_logs)
    if len(logs) > count:
      response.offset.request_id = str(logs[-2]['id']).encode('utf-8')

  @apiproxy_stub.Synchronized
  def _Dynamic_AddRequestInfo(
      self, request, unused_response, unused_request_id):
    """Adds a RequestLog to the local SQLite3 log db.

    Args:
      request: An instance of log_stub_service_pb2.AddRequestInfoRequest.
    """
    log = request.request_log
    items = {
        'module': log.module_id,
        'version_id': log.version_id,
        'start_time': log.start_time,
        'end_time': log.end_time,
        'ip': log.ip,
        'nickname': log.nickname,
        'latency': log.latency,
        'mcycles': log.mcycles,
        'method': log.method,
        'resource': log.resource,
        'http_version': log.http_version,
        'response_size': log.response_size,
        'user_agent': log.user_agent,
        'finished': log.finished,
        'user_request_id': log.request_id,
        'app_id': log.app_id,
        'url_map_entry': log.url_map_entry,
        'host': log.host,
        'status': log.status,
        'referrer': log.referrer
    }
    query = (
        'INSERT OR REPLACE INTO RequestLogs ({keys}) VALUES ({values})'.format(
            keys=', '.join(list(items.keys())),
            values=', '.join(['?'] * len(items))))

    cursor = self._conn.execute(query, list(items.values()))
    self._request_id_to_request_row_id[
        request.request_log.request_id] = cursor.lastrowid
    self._maybe_commit()

  @apiproxy_stub.Synchronized
  def _Dynamic_AddAppLogLine(self, request, unused_response, unused_request_id):
    """Adds a log_service_pb2.LogLine to the AppLogs table.

    Args:
      request: An instance of log_stub_service_pb2.AddAppLogLineRequest.
    """
    self._insert_app_logs(request.request_id, [request.log_line])

  @apiproxy_stub.Synchronized
  def _Dynamic_StartRequestLog(
      self, request, unused_response, unused_request_id):
    """Starts logging for a request.

    Each StartRequestLog call must be followed by a corresponding EndRequestLog
    call to cleanup resources allocated in StartRequestLog.

    Args:
      request: An instance of log_stub_service_pb2.StartRequestLogRequest.
    """
    self.start_request(
        request_id=request.request_id,
        user_request_id=request.user_request_id,
        ip=request.ip,
        app_id=request.app_id,
        version_id=request.version_id,
        nickname=request.nickname,
        user_agent=request.user_agent,
        host=request.host,
        method=request.method,
        resource=request.resource,
        http_version=request.http_version,
        start_time=request.start_time if request.start_time else None,
        module=request.module if request.module else None)

  @apiproxy_stub.Synchronized
  def _Dynamic_EndRequestLog(
      self, request, unused_response, unused_request_id):
    """Ends logging for a request.

    Args:
      request: An instance of log_stub_service_pb2.EndRequestLogRequest.
    """
    self.end_request(
        request.request_id, request.status, request.response_size)

  def _debug_query(self, filter_string, values, result_count):
    for l in self._conn.execute('SELECT * FROM RequestLogs'):
      logging.debug('%r %r %d %d %s', l['module'], l['version_id'],
                    l['start_time'], l['end_time'],
                    l['finished'] and 'COMPLETE' or 'INCOMPLETE')
    for l in self._conn.execute('SELECT * FROM AppLogs'):
      logging.debug('%s %s %s %s %s', l['request_id'], l['timestamp'],
                    l['level'], l['message'],
                    l['id'])

  def _fill_request_log(self, log_row, log, include_app_logs):
    log.request_id = str(log_row['user_request_id']).encode('utf-8')
    log.app_id = log_row['app_id']
    log.version_id = log_row['version_id']
    log.module_id = log_row['module']
    log.ip = log_row['ip']
    log.nickname = log_row['nickname']
    log.start_time = log_row['start_time']
    log.host = log_row['host']
    log.end_time = log_row['end_time']
    log.method = log_row['method']
    log.resource = log_row['resource']
    log.status = log_row['status']
    log.response_size = log_row['response_size']
    log.http_version = log_row['http_version']
    log.user_agent = log_row['user_agent']
    log.url_map_entry = log_row['url_map_entry']
    log.latency = log_row['latency']
    log.mcycles = log_row['mcycles']
    log.finished = log_row['finished']
    log.offset.request_id = str(log_row['id']).encode('utf-8')
    log.combined = _format_combined_field(log_row)
    if include_app_logs:
      log_messages = self._conn.execute(
          'SELECT timestamp, level, message FROM AppLogs '
          'WHERE request_id = ?',
          (log_row['id'],)).fetchall()
      for message in log_messages:
        line = log.line.add()
        line.time = message['timestamp']
        line.level = message['level']
        line.log_message = message['message']

  @staticmethod
  def _extract_read_filters(request):
    """Extracts SQL filters from the LogReadRequest.

    Args:
      request: the incoming LogReadRequest.
    Returns:
      a pair of (filters, values); filters is a list of SQL filter expressions,
      to be joined by AND operators; values is a list of values to be
      interpolated into the filter expressions by the db library.
    """
    filters = []
    values = []

    module_filters = []
    module_values = []
    for module_version in request.module_version:
      module_filters.append('(version_id = ? AND module = ?)')
      module_values.append(module_version.version_id)
      module = appinfo.DEFAULT_MODULE
      if module_version.HasField('module_id'):
        module = module_version.module_id
      module_values.append(module)
    if module_filters:
      filters.append('(' + ' or '.join(module_filters) + ')')
      values += module_values

    if request.HasField('offset'):
      try:
        filters.append('RequestLogs.id < ?')
        values.append(int(request.offset.request_id))
      except ValueError:
        logging.error('Bad offset in log request: "%s"', request.offset)
        raise apiproxy_errors.ApplicationError(
            log_service_pb2.LogServiceError.INVALID_REQUEST)
    if request.HasField('minimum_log_level'):
      filters.append('AppLogs.level >= ?')
      values.append(request.minimum_log_level)






    finished_filter = 'finished = 1 '
    finished_filter_values = []
    unfinished_filter = 'finished = 0'
    unfinished_filter_values = []

    if request.HasField('start_time'):
      finished_filter += ' and end_time >= ? '
      finished_filter_values.append(request.start_time)
      unfinished_filter += ' and start_time >= ? '
      unfinished_filter_values.append(request.start_time)
    if request.HasField('end_time'):
      finished_filter += ' and end_time < ? '
      finished_filter_values.append(request.end_time)
      unfinished_filter += ' and start_time < ? '
      unfinished_filter_values.append(request.end_time)

    if request.include_incomplete:
      filters.append(
          '((' + finished_filter + ') or (' + unfinished_filter + '))')
      values += finished_filter_values + unfinished_filter_values
    else:
      filters.append(finished_filter)
      values += finished_filter_values

    return filters, values

  def _Dynamic_Usage(self, unused_request, unused_response, unused_request_id):
    raise apiproxy_errors.CapabilityDisabledError('Usage not allowed in tests.')

  @apiproxy_stub.Synchronized
  def Clear(self):
    self._conn.execute('DROP TABLE RequestLogs')
    self._conn.execute('DROP TABLE AppLogs')
    self._init_sqlite3_conn()


def _format_combined_field(log_row):
  """Formats the combined field for log_service_pb2.RequestLog.

  Args:
    log_row: A instance of sqlite3.Row containing data from the RequestLogs
      table.

  Returns:
    A string representing the combined field in log_service_pb2.RequestLog.
  """
  time_seconds = (log_row['end_time'] or log_row['start_time']) / 10**6


  date_string = datetime.datetime.utcfromtimestamp(time_seconds).strftime(
      '%d/%b/%Y:%H:%M:%S') + ' +0000'

  combined = (
      '{ip} - {nickname} [{date}] "{method} {resource} {http_version}" '
      '{status} {response_size} {referrer} {user_agent}').format(
          ip=log_row['ip'] or '-',
          nickname=log_row['nickname'] or '-',
          date=date_string,
          method=log_row['method'],
          resource=log_row['resource'],
          http_version=log_row['http_version'],
          status=log_row['status'] or 0,
          response_size=log_row['response_size'],
          referrer=_format_combined_datum_with_quotes(log_row['referrer']),
          user_agent=_format_combined_datum_with_quotes(log_row['user_agent']))

  return combined


def _format_combined_datum_with_quotes(datum):
  """Adds quotes to a field if it is not empty, otherwise returns a dash."""
  if datum:
    return '"' + datum + '"'
  else:
    return '-'
