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
"""WSGI app for the administrative UI."""



import google
import six.moves.urllib
import webapp2

from google.appengine.tools.devappserver2.admin import blobstore_viewer
from google.appengine.tools.devappserver2.admin import console
from google.appengine.tools.devappserver2.admin import cron_handler
from google.appengine.tools.devappserver2.admin import datastore_indexes_viewer
from google.appengine.tools.devappserver2.admin import datastore_stats_handler
from google.appengine.tools.devappserver2.admin import datastore_viewer
from google.appengine.tools.devappserver2.admin import mail_request_handler
from google.appengine.tools.devappserver2.admin import memcache_viewer
from google.appengine.tools.devappserver2.admin import modules_handler
from google.appengine.tools.devappserver2.admin import quit_handler
from google.appengine.tools.devappserver2.admin import search_handler
from google.appengine.tools.devappserver2.admin import static_file_handler
from google.appengine.tools.devappserver2.admin import taskqueue_queues_handler
from google.appengine.tools.devappserver2.admin import taskqueue_tasks_handler


class AdminApplication(webapp2.WSGIApplication):
  """A WSGI application that serves an administrative UI for the application."""

  def __init__(self, dispatch, configuration, host, port, enable_console):
    """Initializer for AdminApplication.

    Args:
      dispatch: A dispatcher.Dispatcher instance used to route requests and
          provide state about running servers.
      configuration: An application_configuration.ApplicationConfiguration
          instance containing the configuration for the application.
      host: The string hostname that the admin server is bound to.
      port: The integer port that the admin server is bound to.
      enable_console: A boolean indicating whether interactive console should
          be enabled.
    """
    super(AdminApplication, self).__init__(
        [('/datastore', datastore_viewer.DatastoreRequestHandler),
         ('/datastore/edit/(.*)', datastore_viewer.DatastoreEditRequestHandler),
         ('/datastore/edit', datastore_viewer.DatastoreEditRequestHandler),
         ('/datastore-indexes',
          datastore_indexes_viewer.DatastoreIndexesViewer),
         ('/datastore-stats', datastore_stats_handler.DatastoreStatsHandler),
         ('/console', console.ConsoleRequestHandler),
         ('/console/restart/(.+)', console.ConsoleRequestHandler.restart),
         ('/memcache', memcache_viewer.MemcacheViewerRequestHandler),
         ('/blobstore', blobstore_viewer.BlobstoreRequestHandler),
         ('/blobstore/blob/(.+)', blobstore_viewer.BlobRequestHandler),
         ('/taskqueue', taskqueue_queues_handler.TaskQueueQueuesHandler),
         ('/taskqueue/queue/(.+)',
          taskqueue_tasks_handler.TaskQueueTasksHandler),
         ('/cron', cron_handler.CronHandler),
         ('/mail', mail_request_handler.MailRequestHandler),
         ('/quit', quit_handler.QuitHandler),
         ('/search', search_handler.SearchIndexesListHandler),
         ('/search/document', search_handler.SearchDocumentHandler),
         ('/search/index', search_handler.SearchIndexHandler),
         ('/assets/(.+)', static_file_handler.StaticFileHandler),
         ('/templates/(.+)', static_file_handler.JsTemplateHandler),
         ('/instances', modules_handler.ModulesHandler),
         webapp2.Route('/',
                       webapp2.RedirectHandler,
                       defaults={'_uri': '/instances'})],
        debug=True)
    self.dispatcher = dispatch
    self.configuration = configuration
    self.host = host
    self.port = port
    self.enable_console = enable_console

  def __call__(self, environ, start_response):
    """Blocks all requests that have an invalid "Origin" header."""
    origin = environ.get('HTTP_ORIGIN')
    if origin:
      parsed_origin = six.moves.urllib.parse.urlparse(origin)
      if (parsed_origin.hostname != self.host or
          parsed_origin.port != self.port):
        start_response('400 Bad Request', [])
        return [
            'The development server\'s admin console only accepts "Origin" '
            'headers if the value matches the admin console\'s host ({}) and '
            'port ({}). Received: {}.'.format(self.host, self.port, origin)]

    return super(AdminApplication, self).__call__(environ, start_response)
