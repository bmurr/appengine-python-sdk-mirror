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
"""Unit tests for the api_request module."""








import google
import gzip
import json
from google.appengine._internal import six
import unittest

from google.appengine.tools.devappserver2.endpoints import api_request
from google.appengine.tools.devappserver2.endpoints import test_utils


class RequestTest(unittest.TestCase):

  def test_parse_no_body(self):
    request = test_utils.build_request('/_ah/api/foo?bar=baz')
    self.assertEqual('foo', request.path)
    self.assertEqual('bar=baz', request.query)
    self.assertEqual({'bar': ['baz']}, request.parameters)
    self.assertEqual(six.ensure_binary(''), request.body)
    self.assertEqual({}, request.body_json)
    self.assertEqual([('CONTENT-TYPE', 'application/json')],
                     request.headers.items())
    self.assertEqual(None, request.request_id)

  def test_parse_with_body(self):
    request = test_utils.build_request('/_ah/api/foo?bar=baz',
                                       six.ensure_binary('{"test": "body"}'))
    self.assertEqual('foo', request.path)
    self.assertEqual('bar=baz', request.query)
    self.assertEqual({'bar': ['baz']}, request.parameters)
    self.assertEqual(six.ensure_binary('{"test": "body"}'), request.body)
    self.assertEqual({'test': 'body'}, request.body_json)
    self.assertEqual([('CONTENT-TYPE', 'application/json')],
                     request.headers.items())
    self.assertEqual(None, request.request_id)

  def test_parse_gzipped_body(self):

    def gzip_encode(content):
      out = six.BytesIO()
      with gzip.GzipFile(fileobj=out, mode='w') as f:
        f.write(content)
      return out.getvalue()

    uncompressed = six.ensure_binary('{"test": "body"}')
    compressed = gzip_encode(uncompressed)
    request = test_utils.build_request('/_ah/api/foo?bar=baz', compressed,
                                       [('Content-encoding', 'gzip')])
    self.assertEqual('foo', request.path)
    self.assertEqual('bar=baz', request.query)
    self.assertEqual({'bar': ['baz']}, request.parameters)
    self.assertEqual(uncompressed, request.body)
    self.assertEqual({'test': 'body'}, request.body_json)
    six.assertCountEqual(self, [('CONTENT-TYPE', 'application/json'),
                                ('CONTENT-ENCODING', 'gzip')],
                         request.headers.items())
    self.assertEqual(None, request.request_id)

  def test_parse_empty_values(self):
    request = test_utils.build_request('/_ah/api/foo?bar')
    self.assertEqual('foo', request.path)
    self.assertEqual('bar', request.query)
    self.assertEqual({'bar': ['']}, request.parameters)
    self.assertEqual(six.ensure_binary(''), request.body)
    self.assertEqual({}, request.body_json)
    self.assertEqual([('CONTENT-TYPE', 'application/json')],
                     request.headers.items())
    self.assertEqual(None, request.request_id)

  def test_parse_multiple_values(self):
    request = test_utils.build_request('/_ah/api/foo?bar=baz&foo=bar&bar=foo')
    self.assertEqual('foo', request.path)
    self.assertEqual('bar=baz&foo=bar&bar=foo', request.query)
    self.assertEqual({
        'bar': ['baz', 'foo'],
        'foo': ['bar']
    }, request.parameters)
    self.assertEqual(six.b(''), request.body)
    self.assertEqual({}, request.body_json)
    self.assertEqual([('CONTENT-TYPE', 'application/json')],
                     request.headers.items())
    self.assertEqual(None, request.request_id)

  def test_is_rpc(self):
    request = test_utils.build_request('/_ah/api/rpc')
    self.assertEqual('rpc', request.path)
    self.assertEqual(None, request.query)
    self.assertTrue(request.is_rpc())

  def test_is_not_rpc(self):
    request = test_utils.build_request('/_ah/api/guestbook/v1/greetings/7')
    self.assertEqual('guestbook/v1/greetings/7', request.path)
    self.assertEqual(None, request.query)
    self.assertFalse(request.is_rpc())

  def teset_is_not_rpc_prefix(self):
    request = test_utils.build_request('/_ah/api/rpcthing')
    self.assertEqual('rpcthing', request.path)
    self.assertEqual(None, request.query)
    self.assertFalse(request.is_rpc())

  def test_batch(self):
    request = test_utils.build_request(
        '/_ah/api/rpc',
        six.ensure_binary('[{"method": "foo", "apiVersion": "v1"}]'))
    self.assertTrue(request.is_batch())
    self.assertNotIsInstance(request.body_json, list)

  def test_batch_too_large(self):
    """Verify that additional items are dropped if the batch size is > 1."""
    request = test_utils.build_request(
        '/_ah/api/rpc',
        six.ensure_binary('[{"method": "foo", "apiVersion": "v1"},'
                          '{"method": "bar", "apiversion": "v1"}]'))
    self.assertTrue(request.is_batch())
    self.assertEqual(
        json.loads('{"method": "foo", "apiVersion": "v1"}'), request.body_json)

  def test_source_ip(self):
    body = six.b('{}')
    path = '/_ah/api/guestbook/v1/greetings'
    env = {
        'SERVER_PORT': 42,
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': 'localhost',
        'HTTP_CONTENT_TYPE': 'application/json',
        'PATH_INFO': path,
        'wsgi.input': six.BytesIO(body)
    }

    request = api_request.ApiRequest(env)
    self.assertEqual(request.source_ip, None)

    env['REMOTE_ADDR'] = '1.2.3.4'
    request = api_request.ApiRequest(env)
    self.assertEqual(request.source_ip, '1.2.3.4')

  def test_copy(self):
    request = test_utils.build_request('/_ah/api/foo?bar=baz',
                                       six.ensure_binary('{"test": "body"}'))
    copied = request.copy()
    self.assertEqual(request.headers.items(), copied.headers.items())
    self.assertEqual(request.body, copied.body)
    self.assertEqual(request.body_json, copied.body_json)
    self.assertEqual(request.path, copied.path)

    copied.headers['Content-Type'] = 'text/plain'
    copied.body = 'Got a whole new body!'
    copied.body_json = {'new': 'body'}
    copied.path = 'And/a/new/path/'

    self.assertNotEqual(request.headers.items(), copied.headers.items())
    self.assertNotEqual(request.body, copied.body)
    self.assertNotEqual(request.body_json, copied.body_json)
    self.assertNotEqual(request.path, copied.path)


if __name__ == '__main__':
  unittest.main()
