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
"""Tests for devappserver2.admin.taskqueue_queues_handler."""

import unittest

import google

from google.appengine.api.taskqueue import taskqueue_service_bytes_pb2
import mox
import webapp2

from google.appengine.tools.devappserver2.admin import admin_request_handler
from google.appengine.tools.devappserver2.admin import taskqueue_queues_handler
from google.appengine.tools.devappserver2.admin import taskqueue_utils

tasks_service_proto = taskqueue_service_bytes_pb2


class TestTaskQueueQueuesHandler(unittest.TestCase):
  """Tests for taskqueue_queues_handler.TaskQueueQueuesHandler."""

  def setUp(self):
    super(TestTaskQueueQueuesHandler, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(taskqueue_utils.QueueInfo, 'get')
    self.mox.StubOutWithMock(admin_request_handler.AdminRequestHandler,
                             'render')
    self.mox.StubOutWithMock(admin_request_handler.AdminRequestHandler, 'get')

  def tearDown(self):
    self.mox.UnsetStubs()
    super(TestTaskQueueQueuesHandler, self).tearDown()

  def test_get(self):
    queue1 = taskqueue_utils.QueueInfo(
        name='queue1',
        mode=tasks_service_proto.TaskQueueMode.PUSH,
        rate='10/s',
        bucket_size=20,
        tasks_in_queue=10,
        oldest_eta_usec=-1)
    queue2 = taskqueue_utils.QueueInfo(
        name='queue1',
        mode=tasks_service_proto.TaskQueueMode.PUSH,
        rate='20/s',
        bucket_size=20,
        tasks_in_queue=10,
        oldest_eta_usec=-1)
    queue3 = taskqueue_utils.QueueInfo(
        name='queue1',
        mode=tasks_service_proto.TaskQueueMode.PULL,
        rate='20/s',
        bucket_size=20,
        tasks_in_queue=10,
        oldest_eta_usec=-1)

    taskqueue_utils.QueueInfo.get().AndReturn([queue1, queue2, queue3])
    request = webapp2.Request.blank('/taskqueue')
    response = webapp2.Response()

    handler = taskqueue_queues_handler.TaskQueueQueuesHandler(request, response)
    admin_request_handler.AdminRequestHandler(handler).get()
    handler.render('taskqueue_queues.html',
                   {'push_queues': [queue1, queue2],
                    'pull_queues': [queue3]})

    self.mox.ReplayAll()
    handler.get()
    self.mox.VerifyAll()

if __name__ == '__main__':
  unittest.main()
