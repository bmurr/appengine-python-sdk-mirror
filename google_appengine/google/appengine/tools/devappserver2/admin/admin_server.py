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
"""Run a server displaying the administrative UI for the application."""



import logging

import google

from google.appengine.tools.devappserver2 import wsgi_server
from google.appengine.tools.devappserver2.admin import admin_app
from google.appengine.tools.devappserver2.admin import admin_request_handler
from google.appengine.tools.devappserver2.admin import console


class AdminServer(wsgi_server.WsgiServer):
  """Serves an administrative UI for the application over HTTP."""

  def __init__(self, host, port, dispatch, configuration, xsrf_token_path,
               enable_host_checking=True, enable_console=False):
    """Initializer for AdminServer.

    Args:
      host: A string containing the name of the host that the server should bind
          to e.g. "localhost".
      port: An int containing the port that the server should bind to e.g. 80.
      dispatch: A dispatcher.Dispatcher instance used to route requests and
          provide state about running servers.
      configuration: An application_configuration.ApplicationConfiguration
          instance containing the configuration for the application.
      xsrf_token_path: A string containing the path to a file that contains the
          XSRF configuration for the admin UI.
      enable_host_checking: A bool indicating that HTTP Host checking should
          be enforced for incoming requests.
      enable_console: A bool indicating that the interactive console should
          be enabled.

    """
    self._host = host
    self._xsrf_token_path = xsrf_token_path

    admin_application = admin_app.AdminApplication(dispatch, configuration,
                                                   host, port, enable_console)
    if enable_host_checking:
      admin_app_module = wsgi_server.WsgiHostCheck([host], admin_application)
    else:
      admin_app_module = admin_application
    super(AdminServer, self).__init__((host, port), admin_app_module)

  def start(self):
    """Start the AdminServer."""
    admin_request_handler.AdminRequestHandler.init_xsrf(self._xsrf_token_path)
    super(AdminServer, self).start()
    logging.info('Starting admin server at: http://%s:%d', self._host,
                 self.port)

  def quit(self):
    """Quits the AdminServer."""
    super(AdminServer, self).quit()
    console.ConsoleRequestHandler.quit()
