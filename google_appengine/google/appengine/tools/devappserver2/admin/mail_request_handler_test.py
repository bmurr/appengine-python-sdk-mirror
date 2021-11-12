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
"""Tests for devappserver2.admin.mail_request_handler."""

import base64
import email.message
import unittest
from unittest import mock

import google
from google.appengine._internal import six
import webapp2

from google.appengine.tools.devappserver2 import dispatcher
from google.appengine.tools.devappserver2.admin import admin_request_handler
from google.appengine.tools.devappserver2.admin import mail_request_handler


class MailRequestHandlerTest(unittest.TestCase):

  def test_generate_email(self):
    message = mail_request_handler.MailRequestHandler._generate_email(
        'to', 'from', 'cc', 'subject', 'body')
    self.assertEqual('from', message['From'])
    self.assertEqual('to', message['To'])
    self.assertEqual('cc', message['Cc'])
    self.assertEqual('subject', message['Subject'])
    text, html = message.get_payload()
    self.assertEqual('text/plain', text.get_content_type())
    self.assertEqual('utf-8', text.get_content_charset())
    content = text.get_payload()
    if text['content-transfer-encoding'] != '7bit':
      if text['content-transfer-encoding'] == 'base64':
        content = base64.b64decode(content)
      else:
        raise Exception('Unrecognized transfer encoding: ' +
                        text['content-transfer-encoding'])
    self.assertEqual(six.ensure_binary('body'), content)

    self.assertEqual('text/html', html.get_content_type())
    self.assertEqual('utf-8', html.get_content_charset())
    content = html.get_payload()
    if text['content-transfer-encoding'] != '7bit':
      if text['content-transfer-encoding'] == 'base64':
        content = base64.b64decode(content)
      else:
        raise Exception('Unexpected transfer encoding: ' +
                        text['content-transfer-encoding'])
    self.assertEqual(six.ensure_binary('body'), content)

  def test_send_email(self):
    response = webapp2.Response()
    handler = mail_request_handler.MailRequestHandler(None, response)
    message = object()
    with mock.patch.object(
        handler,
        '_send',
        return_value=dispatcher.ResponseTuple('500 Internal Server Error', [],
                                              'Response')) as mock_send:
      with mock.patch.object(
          handler, '_generate_email',
          return_value=message) as mock_generate_email:
        handler._send_email('to', 'from', 'cc', 'subject', 'body')

    mock_generate_email.assert_called_with('to', 'from', 'cc', 'subject',
                                           'body')
    mock_send.assert_called_with('/_ah/mail/to', message)
    self.assertEqual(500, response.status_int)

  def test_send(self):
    with mock.patch.object(
        mail_request_handler.MailRequestHandler,
        'dispatcher',
        spec=dispatcher.Dispatcher) as mock_dispatcher:
      handler = mail_request_handler.MailRequestHandler(None, None)
      message = mock.Mock(spec=email.message.Message)
      message.as_string.return_value = 'mail message'

      handler._send('URL', message)

    mock_dispatcher.add_request.assert_called_with(
        method='POST',
        relative_url='URL',
        headers=[('Content-Type', 'message/rfc822')],
        body='mail message',
        source_ip='0.1.0.20')

  def test_get(self):
    request = webapp2.Request.blank('/mail')
    response = webapp2.Response()
    handler = mail_request_handler.MailRequestHandler(request, response)
    with mock.patch.object(admin_request_handler.AdminRequestHandler,
                           'get') as mock_get:
      with mock.patch.object(admin_request_handler.AdminRequestHandler,
                             'render') as mock_render:
        handler.get()

    mock_get.assert_called()
    mock_render.assert_called_with('mail.html', {})

  def test_post(self):
    request = webapp2.Request.blank(
        '/mail',
        POST={
            'to': 'to',
            'from': 'from',
            'cc': 'cc',
            'subject': 'subject',
            'body': 'body'
        })
    response = webapp2.Response()
    handler = mail_request_handler.MailRequestHandler(request, response)

    with mock.patch.object(handler, '_send_email') as mock_send:
      with mock.patch.object(admin_request_handler.AdminRequestHandler,
                             'post') as mock_post:
        handler.post()

    mock_send.assert_called_with('to', 'from', 'cc', 'subject', 'body')
    mock_post.assert_called()


if __name__ == '__main__':
  unittest.main()
