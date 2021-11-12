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
"""Tests for google.appengine.tools.devappserver2.gcs_server."""

import io
import unittest
from unittest import mock

import google
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
if six.PY2:
  from google.appengine.ext.cloudstorage import stub_dispatcher
else:
  from cloudstorage import stub_dispatcher

from google.appengine.tools.devappserver2 import gcs_server
from google.appengine.tools.devappserver2 import wsgi_test_utils


class FakeResult(object):

  def __init__(self, status, headers, content):
    self.status_code = status
    self.headers = headers
    self.content = content


class GCSTest(wsgi_test_utils.WSGITestCase):
  """Tests GCS url handler."""

  def setUp(self):
    super(GCSTest, self).setUp()
    self.app = gcs_server.Application()
    self._host = 'localhost'

  def run_request(self, method, headers, path, query, body, expected_status,
                  expected_headers, expected_content):
    environ = {
        'HTTP_HOST': self._host,
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query,
        'wsgi.url_scheme': 'http',
        'wsgi.input': io.BytesIO(six.ensure_binary(body)),
        'wsgi.input_terminated': True
    }

    for k, v in headers.items():
      environ['HTTP_%s' % k.upper()] = v

    self.assertResponse(expected_status, expected_headers, expected_content,
                        self.app, environ)

  def expect_dispatch_args(self, method, headers, path, body):
    """Setup a mox expectation to gcs_dispatch.dispatch."""

    # webob always adds Host header and optionally adds Content-Length header
    # for requests with non-empty body.
    new_headers = headers.copy()
    new_headers['Host'] = self._host
    # In python 3, the Content-Length is always included.
    if six.PY3 or body:
      new_headers['Content-Length'] = str(len(body))

    url = 'http://%s%s' % (self._host, path)
    return (method, new_headers, url, body)

  def test_dispatch(self):
    """Tests that dispatch stub is called with the correct parameters."""
    result = FakeResult(404, {'a': 'b'}, 'blah')
    with mock.patch.object(
        stub_dispatcher, 'dispatch', return_value=result) as dispatch_mock:
      self.run_request('POST', {'Foo': 'bar'}, '/_ah/gcs/some_bucket',
                       'param=1', 'body', '404 Not Found', [('a', 'b')], 'blah')

    dispatch_mock.assert_called_with(*self.expect_dispatch_args(
        'POST', {'Foo': 'bar'}, '/_ah/gcs/some_bucket?param=1', six.b('body')))

  def test_http_308(self):
    """Tests that the non-standard HTTP 308 status code is handled properly."""
    result = FakeResult(308, {}, '')
    with mock.patch.object(
        stub_dispatcher, 'dispatch', return_value=result) as dispatch_mock:
      self.run_request('GET', {}, '/_ah/gcs/some_bucket', '', '',
                       '308 Resume Incomplete', [], '')

    dispatch_mock.assert_called_with(*self.expect_dispatch_args(
        'GET', {}, '/_ah/gcs/some_bucket', six.b('')))

  def test_dispatch_value_error(self):
    """Tests that ValueError raised by dispatch stub is handled properly."""
    error = ValueError('Invalid Token', six.moves.http_client.BAD_REQUEST)
    with mock.patch.object(
        stub_dispatcher, 'dispatch', side_effect=error) as dispatch_mock:
      self.run_request('GET', {}, '/_ah/some_bucket', '', '', '400 Bad Request',
                       [], 'Invalid Token')

    dispatch_mock.assert_called_once()


if __name__ == '__main__':
  unittest.main()
