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
"""A datastore stats generator button UI."""

import google

# pylint: disable=g-import-not-at-top
from google.appengine.datastore import datastore_stats_generator

from google.appengine.tools.devappserver2.admin import admin_request_handler


class DatastoreStatsHandler(admin_request_handler.AdminRequestHandler):

  def get(self):
    super(DatastoreStatsHandler, self).get()
    self.response.write(self.render('datastore_stats.html', {}))

  def post(self):
    super(DatastoreStatsHandler, self).post()
    if self.request.get('action:compute_stats'):
      msg = datastore_stats_generator.DatastoreStatsProcessor().Run().Report()
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.write(msg)
    else:
      self.response.status_int = 400
