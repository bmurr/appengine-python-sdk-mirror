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
"""A simple handler to serve static assets."""

import logging
import mimetypes
import os
import os.path
import threading

import google

from google.appengine.tools.devappserver2.admin import admin_request_handler

ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
JS_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')


class StaticFileHandler(admin_request_handler.AdminRequestHandler):
  """A request handler for returning static files."""

  _asset_name_to_path = None
  _asset_name_to_path_lock = threading.Lock()

  @classmethod
  def _initialize_asset_map(cls):
    # Generating a list of acceptable asset files reduces the possibility of
    # path attacks.
    cls._asset_name_to_path = {}
    assets = os.listdir(ASSETS_PATH)
    for asset in assets:
      path = os.path.join(ASSETS_PATH, asset)
      if os.path.isfile(path):
        cls._asset_name_to_path[os.path.basename(path)] = path

  def get(self, asset_name):
    """Serve out the contents of a file to self.response.

    Args:
      asset_name: The name of the static asset to serve. Must be in ASSETS_PATH.
    """
    super(StaticFileHandler, self).get(asset_name)
    with self._asset_name_to_path_lock:
      if self._asset_name_to_path is None:
        self._initialize_asset_map()

    if asset_name in self._asset_name_to_path:
      asset_path = self._asset_name_to_path[asset_name]
      try:
        with open(asset_path, 'rb') as f:
          data = f.read()
      except (OSError, IOError):
        logging.exception('Error reading file %s', asset_path)
        self.response.set_status(500)
      else:
        content_type, _ = mimetypes.guess_type(asset_path)
        assert content_type, (
            'cannot determine content-type for %r' % asset_path
        )
        self.response.headers['Content-Type'] = content_type
        self.response.out.write(data)
    else:
      self.response.set_status(404)


class JsTemplateHandler(admin_request_handler.AdminRequestHandler):
  """A request handler returning templated JS files."""

  def get(self, template_name):
    """Renders and serves a JS file to self.response.

    Args:
      template_name: The name of the JS template to render and serve. Must be in
          JS_TEMPLATES_PATH.
    """
    if not template_name.endswith('.js'):
      self.response.set_status(404)
      return

    context = {'modules': [module for module in self.dispatcher.modules
                           if module.supports_interactive_commands]}
    self.response.write(self.render(template_name, context))

