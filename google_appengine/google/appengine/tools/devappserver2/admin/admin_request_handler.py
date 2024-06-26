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
"""A base class for all Admin UI request handlers and related utilities."""

import os.path
import random
import string

import google
import jinja2
from google.appengine._internal import six
import six.moves.urllib
import webapp2

from google.appengine.tools.devappserver2 import metrics
from google.appengine.tools.devappserver2 import util


def _urlencode_filter(value):
  if isinstance(value, six.string_types):
    return six.moves.urllib.parse.quote(value)
  else:
    return six.moves.urllib.parse.urlencode(value)


def _byte_size_format(value):
  byte_count = int(value)
  if byte_count == 1:
    return '1 Byte'
  elif byte_count < 1024:
    return '%d Bytes' % byte_count
  elif byte_count < 1024**2:
    return '%.1f KiB (%d Bytes)' % (byte_count / 1024.0, byte_count)
  elif byte_count < 1024**3:
    return '%.1f MiB (%d Bytes)' % (byte_count / 1024.0**2, byte_count)
  else:
    return '%.1f GiB (%d Bytes)' % (byte_count / 1024.0**3, byte_count)


_TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'templates'))
admin_template_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATE_PATH), autoescape=True)
admin_template_environment.filters['urlencode'] = _urlencode_filter
admin_template_environment.filters['bytesizeformat'] = _byte_size_format


class AdminRequestHandler(webapp2.RequestHandler):
  """Base class for all admin UI request handlers."""

  _SDK_VERSION = util.get_sdk_version()

  @classmethod
  def init_xsrf(cls, xsrf_path):
    """Load the XSRF token from the given path."""
    if os.path.exists(xsrf_path):
      with open(xsrf_path, 'r') as token_file:
        cls.xsrf_token = token_file.read().strip()
    else:
      cls.xsrf_token = ''.join(
          random.choice(string.ascii_letters) for _ in range(10))
      with open(xsrf_path, 'w') as token_file:
        token_file.write(cls.xsrf_token)

  def dispatch(self):
    if self.request.method in [
        'PATCH', 'POST', 'PUT', 'DELETE'
    ] and (self.request.get('xsrf_token') != self.xsrf_token):
      self.response.set_status(403, 'Invalid XSRF token')
      self.response.out.write('<h1>Invalid XSRF token</h1>')
    else:
      super(AdminRequestHandler, self).dispatch()

  def render(self, template, context):
    """Returns a rendered version of the given jinja2 template.

    Args:
      template: The file name of the template file to use e.g.
        "memcache_viewer.html".
      context: A dict of values to use when rendering the template.

    Returns:
      A Unicode object containing the rendered template.
    """
    template = admin_template_environment.get_template(template)
    values = self._get_default_template_values()
    values.update(context)

    return template.render(values)

  def _get_default_template_values(self):
    """Returns default values supplied to all rendered templates."""
    return {
        'app_id': self.configuration.app_id,
        'request': self.request,
        'sdk_version': self._SDK_VERSION,
        'xsrf_token': self.xsrf_token,
        'enable_console': self.enable_console
    }

  def _construct_url(self, remove=None, add=None):
    """Returns a URL referencing the current resource with the same params.

    For example, if the request URL is
    "http://foo/bar?animal=cat&color=redirect" then
    _construct_url(['animal'], {'vehicle': 'car'}) will return
    "http://foo/bar?color=redirect&vehicle=car"

    Args:
      remove: A sequence of query parameters to remove from the query string.
      add: A mapping of query parameters to add to the query string.

    Returns:
      A new query string suitable for use in "GET" requests.
    """
    remove = remove or []
    add = add or {}
    params = dict(self.request.params)
    for arg in remove:
      if arg in params:
        del params[arg]

    params.update(add)
    return str('%s?%s' %
               (self.request.path,
                six.moves.urllib.parse.urlencode(sorted(params.items()))))

  @property
  def dispatcher(self):
    return self.request.app.dispatcher

  @property
  def configuration(self):
    return self.request.app.configuration

  @property
  def enable_console(self):
    return self.request.app.enable_console

  @metrics.LogHandlerRequest(metrics.ADMIN_CONSOLE_CATEGORY)
  def get(self, *args, **kwargs):
    """Base method for all get requests."""
    self.response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    self.response.headers.add('X-XSS-Protection', '1; mode=block')
    self.response.headers.add('Content-Security-Policy', "default-src 'self'")
    self.response.headers.add('Content-Security-Policy',
                              "frame-ancestors 'none'")

  @metrics.LogHandlerRequest(metrics.ADMIN_CONSOLE_CATEGORY)
  def post(self, *args, **kwargs):
    """Base method for all post requests."""
