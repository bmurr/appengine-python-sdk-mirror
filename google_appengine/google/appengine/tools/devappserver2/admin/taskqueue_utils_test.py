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
"""Tests for devappserver2.admin.taskqueue_utils."""



import re
import unittest
from unittest import mock

import google
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
if six.PY2:
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api.taskqueue import taskqueue_service_pb
else:
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api.taskqueue import taskqueue_service_bytes_pb2

from google.appengine.tools.devappserver2.admin import taskqueue_utils


@unittest.skipIf(not six.PY2, 'Requires PY2')
class TestQueueInfoPy2(unittest.TestCase):
  """Tests for taskqueue_queues_handler._QueueInfo."""

  def test_construction(self):
    queue = taskqueue_service_pb.TaskQueueFetchQueuesResponse_Queue()
    queue.set_queue_name('queue1')
    queue.set_mode(taskqueue_service_pb.TaskQueueMode.PUSH)
    queue.set_user_specified_rate('20/s')
    queue.set_bucket_capacity(10)

    queue_stats = (
        taskqueue_service_pb.TaskQueueFetchQueueStatsResponse_QueueStats())
    queue_stats.set_num_tasks(25)
    queue_stats.set_oldest_eta_usec(123 * 10**6)

    info = taskqueue_utils.QueueInfo._from_queue_and_stats(queue, queue_stats)
    self.assertEqual('queue1', info.name)
    self.assertEqual(taskqueue_service_pb.TaskQueueMode.PUSH, info.mode)
    self.assertEqual('20/s', info.rate)
    self.assertEqual(10, info.bucket_size)
    self.assertEqual(25, info.tasks_in_queue)
    self.assertEqual(123 * 10**6, info.oldest_eta_usec)
    self.assertEqual('1970/01/01 00:02:03', info.human_readable_oldest_task_eta)
    self.assertIsNotNone(
        re.match(r'\d+ days, \d{1,2}:\d{1,2}:\d{1,2} ago',
                 info.human_readable_oldest_task_eta_delta))

  def test_get(self):
    fetch_queue_request = taskqueue_service_pb.TaskQueueFetchQueuesRequest()
    fetch_queue_request.set_max_rows(1000)
    fetch_queue_response = taskqueue_service_pb.TaskQueueFetchQueuesResponse()
    queue1 = fetch_queue_response.add_queue()
    queue1.set_queue_name('queue1')
    queue1.set_mode(taskqueue_service_pb.TaskQueueMode.PUSH)
    queue1.set_user_specified_rate('20/s')
    queue1.set_bucket_capacity(10)
    queue2 = fetch_queue_response.add_queue()
    queue2.set_queue_name('queue2')
    queue2.set_mode(taskqueue_service_pb.TaskQueueMode.PULL)
    queue2.set_user_specified_rate('20/s')
    queue2.set_bucket_capacity(10)

    queue_stats_request = taskqueue_service_pb.TaskQueueFetchQueueStatsRequest()
    queue_stats_request.add_queue_name('queue1')
    queue_stats_request.add_queue_name('queue2')
    queue_stats_response = (
        taskqueue_service_pb.TaskQueueFetchQueueStatsResponse())
    queue_stats1 = queue_stats_response.add_queuestats()
    queue_stats1.set_num_tasks(20)
    queue_stats1.set_oldest_eta_usec(-1)
    queue_stats2 = queue_stats_response.add_queuestats()
    queue_stats2.set_num_tasks(50)
    queue_stats2.set_oldest_eta_usec(1234567890)

    def fake_make_sync_call(_, request_name, unused_2, response):
      responses = {
          'FetchQueues': fetch_queue_response,
          'FetchQueueStats': queue_stats_response
      }
      response.CopyFrom(responses[request_name])

    with mock.patch.object(
        apiproxy_stub_map, 'MakeSyncCall',
        side_effect=fake_make_sync_call) as mock_make_sync_call:
      queues = list(taskqueue_utils.QueueInfo.get())

    self.assertEqual('queue1', queues[0].name)
    self.assertEqual('queue2', queues[1].name)
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueues',
                                        fetch_queue_request, mock.ANY)
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueueStats',
                                        queue_stats_request, mock.ANY)

  def test_get_with_queue_name(self):
    fetch_queue_request = taskqueue_service_pb.TaskQueueFetchQueuesRequest()
    fetch_queue_request.set_max_rows(1000)
    fetch_queue_response = taskqueue_service_pb.TaskQueueFetchQueuesResponse()
    queue1 = fetch_queue_response.add_queue()
    queue1.set_queue_name('queue1')
    queue1.set_mode(taskqueue_service_pb.TaskQueueMode.PUSH)
    queue1.set_user_specified_rate('20/s')
    queue1.set_bucket_capacity(10)
    queue2 = fetch_queue_response.add_queue()
    queue2.set_queue_name('queue2')
    queue2.set_mode(taskqueue_service_pb.TaskQueueMode.PULL)
    queue2.set_user_specified_rate('20/s')
    queue2.set_bucket_capacity(10)

    queue_stats_request = taskqueue_service_pb.TaskQueueFetchQueueStatsRequest()
    queue_stats_request.add_queue_name('queue1')
    queue_stats_request.add_queue_name('queue2')
    queue_stats_response = (
        taskqueue_service_pb.TaskQueueFetchQueueStatsResponse())
    queue_stats1 = queue_stats_response.add_queuestats()
    queue_stats1.set_num_tasks(20)
    queue_stats1.set_oldest_eta_usec(-1)
    queue_stats2 = queue_stats_response.add_queuestats()
    queue_stats2.set_num_tasks(50)
    queue_stats2.set_oldest_eta_usec(1234567890)

    def fake_make_sync_call(_, request_name, unused_2, response):
      responses = {
          'FetchQueues': fetch_queue_response,
          'FetchQueueStats': queue_stats_response
      }
      response.CopyFrom(responses[request_name])

    with mock.patch.object(
        apiproxy_stub_map, 'MakeSyncCall',
        side_effect=fake_make_sync_call) as mock_make_sync_call:
      queues = list(taskqueue_utils.QueueInfo.get(frozenset(['queue1'])))

    self.assertEqual('queue1', queues[0].name)
    self.assertEqual(1, len(queues))
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueues',
                                        fetch_queue_request, mock.ANY)
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueueStats',
                                        queue_stats_request, mock.ANY)


@unittest.skipIf(not six.PY3, 'Requires PY3')
class TestQueueInfoPy3(unittest.TestCase):
  """Tests for taskqueue_queues_handler._QueueInfo."""

  def test_construction(self):
    queue = taskqueue_service_bytes_pb2.TaskQueueFetchQueuesResponse.Queue()
    queue.queue_name = six.ensure_binary('queue1')
    queue.mode = taskqueue_service_bytes_pb2.TaskQueueMode.PUSH
    queue.user_specified_rate = '20/s'
    queue.bucket_capacity = 10

    queue_stats = (
        taskqueue_service_bytes_pb2.TaskQueueFetchQueueStatsResponse.QueueStats(
        ))
    queue_stats.num_tasks = 25
    queue_stats.oldest_eta_usec = 123 * 10**6

    info = taskqueue_utils.QueueInfo._from_queue_and_stats(queue, queue_stats)
    self.assertEqual(six.ensure_binary('queue1'), info.name)
    self.assertEqual(taskqueue_service_bytes_pb2.TaskQueueMode.PUSH, info.mode)
    self.assertEqual('20/s', info.rate)
    self.assertEqual(10, info.bucket_size)
    self.assertEqual(25, info.tasks_in_queue)
    self.assertEqual(123 * 10**6, info.oldest_eta_usec)
    self.assertEqual('1970/01/01 00:02:03', info.human_readable_oldest_task_eta)
    self.assertIsNotNone(
        re.match(r'\d+ days, \d{1,2}:\d{1,2}:\d{1,2} ago',
                 info.human_readable_oldest_task_eta_delta))

  def test_get(self):
    fetch_queue_request = taskqueue_service_bytes_pb2.TaskQueueFetchQueuesRequest(
    )
    fetch_queue_request.max_rows = 1000
    fetch_queue_response = taskqueue_service_bytes_pb2.TaskQueueFetchQueuesResponse(
    )
    queue1 = fetch_queue_response.queue.add()
    queue1.queue_name = six.ensure_binary('queue1')
    queue1.mode = taskqueue_service_bytes_pb2.TaskQueueMode.PUSH
    queue1.user_specified_rate = '20/s'
    queue1.bucket_capacity = 10
    queue2 = fetch_queue_response.queue.add()
    queue2.queue_name = six.ensure_binary('queue2')
    queue2.mode = taskqueue_service_bytes_pb2.TaskQueueMode.PULL
    queue2.user_specified_rate = '20/s'
    queue2.bucket_capacity = 10

    queue_stats_request = taskqueue_service_bytes_pb2.TaskQueueFetchQueueStatsRequest(
    )
    queue_stats_request.queue_name.append(six.ensure_binary('queue1'))
    queue_stats_request.queue_name.append(six.ensure_binary('queue2'))
    queue_stats_response = (
        taskqueue_service_bytes_pb2.TaskQueueFetchQueueStatsResponse())
    queue_stats1 = queue_stats_response.queuestats.add()
    queue_stats1.num_tasks = 20
    queue_stats1.oldest_eta_usec = -1
    queue_stats2 = queue_stats_response.queuestats.add()
    queue_stats2.num_tasks = 50
    queue_stats2.oldest_eta_usec = 1234567890

    def fake_make_sync_call(_, request_name, unused_2, response):
      responses = {
          'FetchQueues': fetch_queue_response,
          'FetchQueueStats': queue_stats_response
      }
      response.CopyFrom(responses[request_name])

    with mock.patch.object(
        apiproxy_stub_map, 'MakeSyncCall',
        side_effect=fake_make_sync_call) as mock_make_sync_call:
      queues = list(taskqueue_utils.QueueInfo.get())

    self.assertEqual(six.ensure_binary('queue1'), queues[0].name)
    self.assertEqual(six.ensure_binary('queue2'), queues[1].name)
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueues',
                                        fetch_queue_request, mock.ANY)
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueueStats',
                                        queue_stats_request, mock.ANY)

  def test_get_with_queue_name(self):
    fetch_queue_request = taskqueue_service_bytes_pb2.TaskQueueFetchQueuesRequest(
    )
    fetch_queue_request.max_rows = 1000
    fetch_queue_response = taskqueue_service_bytes_pb2.TaskQueueFetchQueuesResponse(
    )
    queue1 = fetch_queue_response.queue.add()
    queue1.queue_name = six.ensure_binary('queue1')
    queue1.mode = taskqueue_service_bytes_pb2.TaskQueueMode.PUSH
    queue1.user_specified_rate = '20/s'
    queue1.bucket_capacity = 10
    queue2 = fetch_queue_response.queue.add()
    queue2.queue_name = six.ensure_binary('queue2')
    queue2.mode = taskqueue_service_bytes_pb2.TaskQueueMode.PULL
    queue2.user_specified_rate = '20/s'
    queue2.bucket_capacity = 10

    queue_stats_request = taskqueue_service_bytes_pb2.TaskQueueFetchQueueStatsRequest(
    )
    queue_stats_request.queue_name.append(six.ensure_binary('queue1'))
    queue_stats_request.queue_name.append(six.ensure_binary('queue2'))
    queue_stats_response = (
        taskqueue_service_bytes_pb2.TaskQueueFetchQueueStatsResponse())
    queue_stats1 = queue_stats_response.queuestats.add()
    queue_stats1.num_tasks = 20
    queue_stats1.oldest_eta_usec = -1
    queue_stats2 = queue_stats_response.queuestats.add()
    queue_stats2.num_tasks = 50
    queue_stats2.oldest_eta_usec = 1234567890

    def fake_make_sync_call(_, request_name, unused_2, response):
      responses = {
          'FetchQueues': fetch_queue_response,
          'FetchQueueStats': queue_stats_response
      }
      response.CopyFrom(responses[request_name])

    with mock.patch.object(
        apiproxy_stub_map, 'MakeSyncCall',
        side_effect=fake_make_sync_call) as mock_make_sync_call:
      queues = list(taskqueue_utils.QueueInfo.get(frozenset([b'queue1'])))

    self.assertEqual(six.ensure_binary('queue1'), queues[0].name)
    self.assertEqual(1, len(queues))
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueues',
                                        fetch_queue_request, mock.ANY)
    mock_make_sync_call.assert_any_call('taskqueue', 'FetchQueueStats',
                                        queue_stats_request, mock.ANY)


if __name__ == '__main__':
  unittest.main()
