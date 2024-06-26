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
"""Tests for devappserver2.admin.console."""

import unittest

import google

import mox
from google.appengine._internal import six
import webapp2

from google.appengine.tools.devappserver2 import dispatcher
from google.appengine.tools.devappserver2 import errors
from google.appengine.tools.devappserver2 import module
from google.appengine.tools.devappserver2.admin import admin_request_handler
from google.appengine.tools.devappserver2.admin import console


class ConsoleRequestHandlerTest(unittest.TestCase):
  """Tests for devappserver2.admin.console.ConsoleRequestHandler."""

  def setUp(self):
    super(ConsoleRequestHandlerTest, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(console.ConsoleRequestHandler, 'dispatcher')
    self.mox.StubOutWithMock(admin_request_handler.AdminRequestHandler, 'post')
    console.ConsoleRequestHandler._modulename_to_shell_module = {}
    self.dispatcher = self.mox.CreateMock(dispatcher.Dispatcher)
    self.module = self.mox.CreateMock(module.Module)
    self.interactive_command_module = self.mox.CreateMock(
        module.InteractiveCommandModule)

  def tearDown(self):
    self.mox.UnsetStubs()
    super(ConsoleRequestHandlerTest, self).tearDown()

  def test_post_new_module(self):
    self.mox.StubOutWithMock(console.ConsoleRequestHandler, 'enable_console')
    request = webapp2.Request.blank('', POST={'code': 'print 5+5',
                                              'module_name': 'default'})
    response = webapp2.Response()

    handler = console.ConsoleRequestHandler(request, response)
    handler.enable_console = True
    admin_request_handler.AdminRequestHandler(handler).post()
    handler.dispatcher = self.dispatcher
    handler.dispatcher.get_module_by_name('default').AndReturn(self.module)
    self.module.create_interactive_command_module().AndReturn(
        self.interactive_command_module)
    self.interactive_command_module.send_interactive_command(
        'print 5+5').AndReturn('10\n')

    self.mox.ReplayAll()
    handler.post()
    self.mox.VerifyAll()
    self.assertEqual(200, response.status_int)
    self.assertEqual(six.ensure_binary('10\n'), response.body)

  def test_post_cached_module(self):
    self.mox.StubOutWithMock(console.ConsoleRequestHandler, 'enable_console')
    console.ConsoleRequestHandler._modulename_to_shell_module = {
        'default': self.interactive_command_module}

    request = webapp2.Request.blank('', POST={'code': 'print 5+5',
                                              'module_name': 'default'})
    response = webapp2.Response()

    handler = console.ConsoleRequestHandler(request, response)
    handler.enable_console = True
    admin_request_handler.AdminRequestHandler(handler).post()
    handler.dispatcher = self.dispatcher
    self.interactive_command_module.send_interactive_command(
        'print 5+5').AndReturn('10\n')

    self.mox.ReplayAll()
    handler.post()
    self.mox.VerifyAll()
    self.assertEqual(200, response.status_int)
    self.assertEqual(six.ensure_binary('10\n'), response.body)

  def test_post_exception(self):
    self.mox.StubOutWithMock(console.ConsoleRequestHandler, 'enable_console')
    console.ConsoleRequestHandler._modulename_to_shell_module = {
        'default': self.interactive_command_module}

    request = webapp2.Request.blank('', POST={'code': 'print 5+5',
                                              'module_name': 'default'})
    response = webapp2.Response()

    handler = console.ConsoleRequestHandler(request, response)
    handler.enable_console = True
    admin_request_handler.AdminRequestHandler(handler).post()
    handler.dispatcher = self.dispatcher
    self.interactive_command_module.send_interactive_command(
        'print 5+5').AndRaise(errors.InteractiveCommandError('restart'))

    self.mox.ReplayAll()
    handler.post()
    self.mox.VerifyAll()
    self.assertEqual(200, response.status_int)
    self.assertEqual(six.ensure_binary('restart'), response.body)

  def test_post_when_console_disabled_fails(self):
    self.mox.StubOutWithMock(console.ConsoleRequestHandler, 'enable_console')
    request = webapp2.Request.blank('', POST={'code': 'print 5+5',
                                              'module_name': 'default'})
    response = webapp2.Response()

    handler = console.ConsoleRequestHandler(request, response)
    handler.enable_console = False
    admin_request_handler.AdminRequestHandler(handler).post()

    self.mox.ReplayAll()
    handler.post()
    self.mox.VerifyAll()
    self.assertEqual(404, response.status_int)
    self.assertIn(
        six.ensure_binary('The interactive console is currently disabled.'),
        response.body)

  def test_restart(self):
    console.ConsoleRequestHandler._modulename_to_shell_module = {
        'default': self.interactive_command_module}

    self.interactive_command_module.restart()

    self.mox.ReplayAll()
    console.ConsoleRequestHandler.restart(webapp2.Request.blank('/'), 'default')
    self.mox.VerifyAll()

  def test_restart_uncached_module(self):
    self.mox.ReplayAll()
    console.ConsoleRequestHandler.restart(webapp2.Request.blank('/'), 'default')
    self.mox.VerifyAll()

  def test_quit(self):
    console.ConsoleRequestHandler._modulename_to_shell_module = {
        'default': self.interactive_command_module}

    self.interactive_command_module.quit()

    self.mox.ReplayAll()
    console.ConsoleRequestHandler.quit()
    self.mox.VerifyAll()

if __name__ == '__main__':
  unittest.main()
