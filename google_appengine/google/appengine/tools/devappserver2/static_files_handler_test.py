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
"""Tests for google.appengine.tools.devappserver2.static_files_handler."""



import datetime
import errno
import os.path
import unittest
from unittest import mock

import google
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
if six.PY2:
  from google.appengine.api import appinfo
else:
  from google.appengine.api import appinfo

from google.appengine.tools.devappserver2 import errors
from google.appengine.tools.devappserver2 import static_files_handler
from google.appengine.tools.devappserver2 import wsgi_test_utils


class TestStaticContentHandlerHandlePath(wsgi_test_utils.WSGITestCase):
  """Tests for static_files_handler.StaticContentHandler._handle_path."""

  def tearDown(self):
    static_files_handler.StaticContentHandler._filename_to_mtime_and_etag = {}
    super(TestStaticContentHandlerHandlePath, self).tearDown()

  def test_load_file(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(
        os.path, 'getmtime', return_value=12345.6) as getmtime_mock:
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!') as read_file_mock:
        self.assertResponse(
            '200 OK', {
                'Content-type': 'text/html',
                'Content-length': '12',
                'Expires': 'Fri, 01 Jan 1990 00:00:00 GMT',
                'Cache-Control': 'public',
                'ETag': '"NDcyNDU2MzU1"'
            }, 'Hello World!', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'GET'})

    getmtime_mock.assert_called_with('/home/appdir/index.html')
    read_file_mock.assert_called_with('/home/appdir/index.html')
    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_load_cached_file(self):
    static_files_handler.StaticContentHandler._filename_to_mtime_and_etag = {
        '/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')
    }

    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse(
            '200 OK', {
                'Content-type': 'text/html',
                'Content-length': '12',
                'Expires': 'Fri, 01 Jan 1990 00:00:00 GMT',
                'Cache-Control': 'public',
                'ETag': '"NDcyNDU2MzU1"'
            }, 'Hello World!', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'GET'})

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_load_head(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse(
            '200 OK', {
                'Content-type': 'text/html',
                'Content-length': '12',
                'Expires': 'Fri, 01 Jan 1990 00:00:00 GMT',
                'Cache-Control': 'public',
                'ETag': '"NDcyNDU2MzU1"'
            }, '', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'HEAD'})

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_no_permission_read(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    error = IOError()
    error.errno = errno.EPERM
    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          side_effect=error):
        self.assertResponse('403 Forbidden', {}, '', h._handle_path,
                            '/home/appdir/index.html', {
                                'REQUEST_METHOD': 'GET',
                                'PATH_INFO': '/'
                            })

  def test_cached_no_permission_read(self):
    static_files_handler.StaticContentHandler._filename_to_mtime_and_etag = {
        '/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')
    }

    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    error = IOError()
    error.errno = errno.EPERM
    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          side_effect=error):
        self.assertResponse('403 Forbidden', {}, '', h._handle_path,
                            '/home/appdir/index.html', {
                                'REQUEST_METHOD': 'GET',
                                'PATH_INFO': '/'
                            })

  def test_file_does_not_exist_read(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    error = IOError()
    error.errno = errno.ENOENT
    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          side_effect=error):
        self.assertResponse('404 Not Found', {}, '', h._handle_path,
                            '/home/appdir/index.html', {
                                'REQUEST_METHOD': 'GET',
                                'PATH_INFO': '/'
                            })

  def test_file_does_not_exist_stat(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    error = IOError()
    error.errno = errno.ENOENT

    with mock.patch.object(os.path, 'getmtime', side_effect=error):
      self.assertResponse('404 Not Found', {}, '', h._handle_path,
                          '/home/appdir/index.html', {
                              'REQUEST_METHOD': 'GET',
                              'PATH_INFO': '/'
                          })

  def test_if_match_without_match(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse('412 Precondition Failed',
                            {'ETag': '"NDcyNDU2MzU1"'}, '', h._handle_path,
                            '/home/appdir/index.html', {
                                'REQUEST_METHOD': 'GET',
                                'HTTP_IF_MATCH': '"nomatch"'
                            })
    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_if_match_no_file(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    error = IOError()
    error.errno = errno.ENOENT
    with mock.patch.object(os.path, 'getmtime', side_effect=error):
      self.assertResponse('412 Precondition Failed', {}, '', h._handle_path,
                          '/home/appdir/index.html', {
                              'REQUEST_METHOD': 'GET',
                              'HTTP_IF_MATCH': '"nomatch"'
                          })
    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {})

  def test_cached_if_match_without_match(self):
    static_files_handler.StaticContentHandler._filename_to_mtime_and_etag = {
        '/home/appdir/index.html': (12345.6, 'abc')
    }

    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      self.assertResponse('412 Precondition Failed', {'ETag': '"abc"'}, '',
                          h._handle_path, '/home/appdir/index.html', {
                              'REQUEST_METHOD': 'GET',
                              'HTTP_IF_MATCH': '"nomatch"'
                          })
    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'abc')})

  def test_if_none_match_with_match(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse('304 Not Modified', {'ETag': '"NDcyNDU2MzU1"'}, '',
                            h._handle_path, '/home/appdir/index.html', {
                                'REQUEST_METHOD': 'GET',
                                'HTTP_IF_NONE_MATCH': '"NDcyNDU2MzU1"'
                            })

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_cached_if_none_match_with_match(self):
    static_files_handler.StaticContentHandler._filename_to_mtime_and_etag = {
        '/home/appdir/index.html': (12345.6, 'match')
    }

    url_map = appinfo.URLMap(url='/', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      self.assertResponse('304 Not Modified', {'ETag': '"match"'}, '',
                          h._handle_path, '/home/appdir/index.html', {
                              'REQUEST_METHOD': 'GET',
                              'HTTP_IF_NONE_MATCH': '"match"'
                          })

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'match')})

  def test_custom_headers(self):
    http_headers = appinfo.HttpHeadersDict()
    http_headers['Content-type'] = 'text/xml'
    http_headers['ETag'] = 'abc123'
    http_headers['Expires'] = 'tomorrow'
    http_headers['Cache-Control'] = 'private'
    http_headers['Custom-Header'] = 'custom,value'

    url_map = appinfo.URLMap(
        url='/', static_files='index.html', http_headers=http_headers)

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse(
            '200 OK', {
                'Content-length': '12',
                'Content-type': 'text/xml',
                'ETag': 'abc123',
                'Expires': 'tomorrow',
                'Cache-Control': 'private',
                'Custom-Header': 'custom,value'
            }, 'Hello World!', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'GET'})

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_custom_mimetype(self):
    url_map = appinfo.URLMap(
        url='/', mime_type='text/xml', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse(
            '200 OK', {
                'Content-type': 'text/xml',
                'Content-length': '12',
                'Expires': 'Fri, 01 Jan 1990 00:00:00 GMT',
                'Cache-Control': 'public',
                'ETag': '"NDcyNDU2MzU1"'
            }, 'Hello World!', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'GET'})

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_custom_expiration_set(self):
    static_files_handler.Now = mock.Mock(
        return_value=datetime.datetime(1990, 0o1, 0o1))

    url_map = appinfo.URLMap(
        url='/', expiration='1d 2h 3m 4s', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse(
            '200 OK', {
                'Content-type': 'text/html',
                'Content-length': '12',
                'ETag': '"NDcyNDU2MzU1"',
                'Expires': 'Tue, 02 Jan 1990 10:03:04 GMT',
                'Cache-Control': 'public'
            }, 'Hello World!', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'GET'})

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_expiration_precedence(self):
    static_files_handler.Now = mock.Mock(
        return_value=datetime.datetime(1990, 0o1, 0o1))

    url_map = appinfo.URLMap(
        url='/', expiration='1d 2h 3m 4s', static_files='index.html')

    h = static_files_handler.StaticContentHandler(
        root_path=None,
        url_map=url_map,
        url_pattern='/$',
        app_info_default_expiration='2d 3h 4m 5s')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='Hello World!'):
        self.assertResponse(
            '200 OK', {
                'Content-type': 'text/html',
                'Content-length': '12',
                'ETag': '"NDcyNDU2MzU1"',
                'Expires': 'Tue, 02 Jan 1990 10:03:04 GMT',
                'Cache-Control': 'public'
            }, 'Hello World!', h._handle_path, '/home/appdir/index.html',
            {'REQUEST_METHOD': 'GET'})

    self.assertEqual(
        static_files_handler.StaticContentHandler._filename_to_mtime_and_etag,
        {'/home/appdir/index.html': (12345.6, 'NDcyNDU2MzU1')})

  def test_nonstandard_mimetype(self):
    url_map = appinfo.URLMap(url='/', static_files='simple.dart')

    h = static_files_handler.StaticContentHandler(
        root_path=None, url_map=url_map, url_pattern='/$')

    with mock.patch.object(os.path, 'getmtime', return_value=12345.6):
      with mock.patch.object(
          static_files_handler.StaticContentHandler,
          '_read_file',
          return_value='void main() {}') as read_file_mock:
        self.assertResponse(
            '200 OK', {
                'Content-type': 'application/dart',
                'Content-length': '14',
                'Expires': 'Fri, 01 Jan 1990 00:00:00 GMT',
                'Cache-Control': 'public',
                'ETag': '"LTE2OTA2MzYyMTM="'
            }, 'void main() {}', h._handle_path, '/home/appdir/simple.dart',
            {'REQUEST_METHOD': 'GET'})

    read_file_mock.assert_called_with('/home/appdir/simple.dart')


class TestStaticContentHandlerCheckEtagMatch(unittest.TestCase):
  """Tests for static_files_handler.StaticContentHandler._check_etag_match."""

  def test_strong_match_required(self):
    self.assertTrue(
        static_files_handler.StaticContentHandler._check_etag_match(
            '"abc"', 'abc', allow_weak_match=False))

  def test_strong_match_no_match(self):
    self.assertFalse(
        static_files_handler.StaticContentHandler._check_etag_match(
            '"nomatch"', 'abc', allow_weak_match=False))

  def test_strong_match_with_weak_tag(self):
    self.assertFalse(
        static_files_handler.StaticContentHandler._check_etag_match(
            'W/"abc"', 'abc', allow_weak_match=False))

  def test_strong_match_star(self):
    self.assertTrue(
        static_files_handler.StaticContentHandler._check_etag_match(
            '*', 'abc', allow_weak_match=False))

  def test_weak_match_required(self):
    self.assertTrue(
        static_files_handler.StaticContentHandler._check_etag_match(
            '"abc"', 'abc', allow_weak_match=True))

  def test_weak_match_no_match(self):
    self.assertFalse(
        static_files_handler.StaticContentHandler._check_etag_match(
            '"nomatch"', 'abc', allow_weak_match=True))

  def test_weak_match_with_weak_tag(self):
    self.assertTrue(
        static_files_handler.StaticContentHandler._check_etag_match(
            'W/"abc"', 'abc', allow_weak_match=True))

  def test_weak_match_star(self):
    self.assertTrue(
        static_files_handler.StaticContentHandler._check_etag_match(
            '*', 'abc', allow_weak_match=True))

  def test_many_etags_match(self):
    self.assertTrue(
        static_files_handler.StaticContentHandler._check_etag_match(
            '"abc", "def", "ghi"', 'def', allow_weak_match=False))

  def test_many_etags_no_match(self):
    self.assertFalse(
        static_files_handler.StaticContentHandler._check_etag_match(
            '"abc", "def", "ghi"', 'jkl', allow_weak_match=False))


class TestStaticFilesHandler(wsgi_test_utils.WSGITestCase):
  """Tests for static_files_handler.StaticFilesHandler."""

  def test_simple_path(self):
    url_map = appinfo.URLMap(url='/', static_files='index.html')
    h = static_files_handler.StaticFilesHandler(
        root_path='/appdir', url_map=url_map)
    match = h.match('/')
    self.assertTrue(match)
    self.assertFalse(h.match('/other'))

    with mock.patch.object(
        static_files_handler.StaticContentHandler,
        '_handle_path',
        return_value='<output>') as handle_path_mock:
      self.assertEqual('<output>', h.handle(match, {}, None))

    handle_path_mock.assert_called_with(
        os.path.join('/appdir', 'index.html'), {}, mock.ANY)

  def test_patterned_path(self):
    url_map = appinfo.URLMap(
        url=r'/(.*)/(.*)', static_files=r'static/\1/subdir/\2')
    h = static_files_handler.StaticFilesHandler(
        root_path='/appdir', url_map=url_map)
    match = h.match('/hello/foo.jpg')
    self.assertTrue(match)
    self.assertFalse(h.match('/'))

    with mock.patch.object(
        static_files_handler.StaticContentHandler,
        '_handle_path',
        return_value='<output>') as handle_path_mock:
      self.assertEqual('<output>', h.handle(match, {}, None))

    handle_path_mock.assert_called_with(
        os.path.join('/appdir', 'static/hello/subdir/foo.jpg'), {}, mock.ANY)

  def test_invalid_regex(self):
    url_map = appinfo.URLMap(url='((.*))(', static_files='index.html')
    with mock.patch.object(static_files_handler.StaticContentHandler,
                           '_handle_path'):
      with self.assertRaises(errors.InvalidAppConfigError):
        static_files_handler.StaticFilesHandler(
            root_path='/appdir', url_map=url_map)


class TestStaticDirHandler(wsgi_test_utils.WSGITestCase):
  """Tests for static_files_handler.StaticDirHandler."""

  def test_simple_path(self):
    url_map = appinfo.URLMap(url='/foo', static_dir='subdir')
    h = static_files_handler.StaticDirHandler(
        root_path='/appdir', url_map=url_map)
    match = h.match('/foo/bar.jpg')
    self.assertTrue(match)
    self.assertFalse(h.match('/baz'))

    with mock.patch.object(
        static_files_handler.StaticContentHandler,
        '_handle_path',
        return_value='<output>') as mock_handle_path:
      self.assertEqual('<output>', h.handle(match, {}, None))

    mock_handle_path.assert_called_with(
        os.path.join('/appdir', 'subdir', 'bar.jpg'), {}, mock.ANY)

  def test_invalid_regex(self):
    url_map = appinfo.URLMap(url='((.*))(', static_files='index.html')
    with mock.patch.object(static_files_handler.StaticContentHandler,
                           '_handle_path'):
      with self.assertRaises(errors.InvalidAppConfigError):
        static_files_handler.StaticDirHandler(
            root_path='/appdir', url_map=url_map)


if __name__ == '__main__':
  unittest.main()
