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
"""A handler that displays queue information for the application."""



import google
from google.appengine._internal import six

# pylint: disable=g-import-not-at-top
if six.PY2:
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api.taskqueue import taskqueue_service_pb
  tasks_service_proto = taskqueue_service_pb
else:
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api.taskqueue import taskqueue_service_bytes_pb2
  tasks_service_proto = taskqueue_service_bytes_pb2

from google.appengine.tools.devappserver2.admin import admin_request_handler
from google.appengine.tools.devappserver2.admin import taskqueue_utils


class TaskQueueQueuesHandler(admin_request_handler.AdminRequestHandler):
  """A handler that displays queue information for the application."""

  def get(self):
    super(TaskQueueQueuesHandler, self).get()
    push_queues = []
    pull_queues = []
    for queue_info in taskqueue_utils.QueueInfo.get():
      if queue_info.mode == tasks_service_proto.TaskQueueMode.PUSH:
        push_queues.append(queue_info)
      elif queue_info.mode == tasks_service_proto.TaskQueueMode.PULL:
        pull_queues.append(queue_info)
      else:
        assert 0, 'unexpected queue type: %r' % queue_info.mode

    self.response.write(
        self.render('taskqueue_queues.html', {
            'push_queues': push_queues,
            'pull_queues': pull_queues
        }))

  def _purge_queue(self, queue_name):
    request = tasks_service_proto.TaskQueuePurgeQueueRequest()
    response = tasks_service_proto.TaskQueuePurgeQueueResponse()
    request.queue_name = queue_name
    apiproxy_stub_map.MakeSyncCall('taskqueue', 'PurgeQueue', request, response)

  def post(self):
    """Handle modifying actions and redirect to a GET page."""
    super(TaskQueueQueuesHandler, self).post()
    queue_name = self.request.get('queue')

    if self.request.get('action:purgequeue'):
      self._purge_queue(queue_name)
    self.redirect(self.request.path_url)
