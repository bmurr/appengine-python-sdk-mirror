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
"""Library with a variant of appengine_rpc using google.auth."""

import logging
import random
import re
import socket
import time

import warnings

from google_auth_oauthlib import flow as oauthlib_flow
import requests
import six.moves
from six.moves import urllib_error
from six.moves import urllib_parse

from google.auth import exceptions
from google.auth.transport import requests as transport
from google.oauth2 import credentials
from google.appengine.tools.value_mixin import ValueMixin

HTTPError = urllib_error.HTTPError

logger = logging.getLogger('google.appengine.tools.appengine_rpc')


_TIMEOUT_WAIT_TIME = 5


class Error(Exception):
  pass


class AuthPermanentFail(Error):
  """Authentication will not succeed in the current context."""


def raise_http_error(url, response, extra_msg=''):
  """Raise a urllib2.HTTPError based on an httplib2 response tuple."""
  if response.content is not None:
    stream = six.moves.StringIO()
    stream.write(six.ensure_str(response.content))
    stream.seek(0)
  else:
    stream = None
  msg = '<no message>'
  msg_args = filter(None, [response.reason, extra_msg])
  if msg_args:
    msg = ' '.join(msg_args)


  raise urllib_error.HTTPError(
      url, response.status_code, msg, response, stream)



class GoogleAuthRpcServer(object):
  """A variant of HttpRpcServer which uses google.auth.

  This variant is specifically meant for interactive command line usage,
  as it will attempt to open a browser and ask the user to enter
  information from the resulting web page.
  """

  class OAuth2Parameters(ValueMixin):
    """Class encapsulating parameters related to OAuth2 authentication."""

    def __init__(
        self, access_token=None, client_id=None, client_secret=None, scope=None,
        refresh_token=None, credential_file=None, token_uri=None,
        credentials=None, auth_uri=None
    ):
      self.access_token = access_token
      self.client_id = client_id
      self.client_secret = client_secret
      self.scopes = scope if isinstance(scope, (tuple, list)) else [scope]
      self.refresh_token = refresh_token
      self.credential_file = credential_file
      self.token_uri = token_uri
      self.auth_uri = auth_uri
      self._credentials = credentials

    def get_credentials(self):
      """Get google.auth credentials."""
      if not self._credentials:
        if any((self.access_token, self.refresh_token, self.token_uri)):
          self._credentials = credentials.Credentials(
              self.access_token, self.refresh_token, client_id=self.client_id,
              client_secret=self.client_secret, token_uri=self.token_uri,
              scopes=self.scopes)
      return self._credentials

    def set_credentials(self, value):
      """Set google.auth credentials, update file if required."""
      self._credentials = value

    def get_flow(self):
      """Get interactive authentication flow."""
      attrs_to_copy = [
          'access_token', 'client_id', 'client_secret', 'refresh_token',
          'token_uri', 'auth_uri']
      config = {k: getattr(self, k) for k in attrs_to_copy}
      if config['token_uri'] is None:
        config['token_uri'] = 'https://oauth2.googleapis.com/token'
      if config['auth_uri'] is None:
        config['auth_uri'] = 'https://accounts.google.com/o/oauth2/auth'
      client_config = {
          'installed': config
      }
      return oauthlib_flow.InstalledAppFlow.from_client_config(
          client_config, self.scopes)

  class FlowFlags(object):

    def __init__(self, options):
      self.logging_level = logging.getLevelName(logging.getLogger().level)
      self.noauth_local_webserver = (
          not options.get('auth_local_webserver', False))
      self.auth_host_port = [8080, 8090]
      self.auth_host_name = 'localhost'

  def __init__(
      self, host, oauth2_parameters, user_agent, source, host_override=None,
      extra_headers=None, save_cookies=False, auth_tries=0,
      account_type=None, debug_data=True, secure=True, ignore_certs=False,
      rpc_tries=3, timeout_max_errors=2, options=None, conflict_max_errors=10,
      http_class=None, http_object=None):
    """Creates a new HttpRpcServerOAuth2.

    Args:
      host: The host to send requests to.
      oauth2_parameters: An object of type AuthParameters (defined above) that
        specifies all parameters related to OAuth2 authentication. (This
        replaces the auth_function parameter in the parent class.)
      user_agent: The user-agent string to send to the server. Specify None to
        omit the user-agent header.
      source: Saved but ignored.
      host_override: The host header to send to the server (defaults to host).
      extra_headers: A dict of extra headers to append to every request. Values
        supplied here will override other default headers that are supplied.
      save_cookies: Ignored.
      auth_tries: The number of times to attempt auth_function before failing.
      account_type: Ignored.
      debug_data: Whether debugging output should include data contents.
      secure: If the requests sent using Send should be sent over HTTPS.
      ignore_certs: Ignored.
      rpc_tries: The number of rpc retries upon http server error (i.e. Response
        code >= 500 and < 600) before failing.
      timeout_max_errors: The number of rpc retries upon http server timeout
        (i.e. Response code 408) before failing.
      options: dict, authentication flow options.
      conflict_max_errors: The number of rpc retries upon http server error
        (i.e. Response code 409) before failing.
      http_class: ignored.
      http_object: ignored. Used to be used by tests only,
        mock self.session.request() instead
    """
    self.host = host
    self.user_agent = user_agent
    self.source = source
    self.extra_headers = extra_headers or {}
    self.save_cookies = save_cookies
    self.auth_max_errors = auth_tries
    self.debug_data = debug_data
    self.secure = secure
    self.ignore_certs = ignore_certs
    self.rpc_max_errors = rpc_tries
    self.scheme = secure and 'https' or 'http'
    self.conflict_max_errors = conflict_max_errors
    self.timeout_max_errors = timeout_max_errors
    self.host_override = host_override

    if http_class or http_object:
      warnings.warn(
          'GoogleAuthRpcServer: Parameters http_class and http_object ignored',
          UserWarning)

    if not isinstance(oauth2_parameters, self.OAuth2Parameters):
      raise TypeError('oauth2_parameters must be an OAuth2Parameters: %r' %
                      oauth2_parameters)
    self.oauth2_parameters = oauth2_parameters

    self.credentials = self.oauth2_parameters.get_credentials()
    if not isinstance(options, dict):
      options = options.__dict__ if options else {}
    self.flags = self.FlowFlags(options)

    self.session = transport.AuthorizedSession(

        max_refresh_attempts=0, refresh_status_codes=[],
        credentials=self.credentials)

    if self.user_agent is not None:
      self.session.headers['User-Agent'] = self.user_agent
    else:
      del self.session.headers['User-Agent']

  def _Authenticate(self):
    """Pre or Re-auth stuff...

    This will attempt to avoid making any OAuth related HTTP connections or
    user interactions unless it's needed.

    Raises:
      AuthPermanentFail: The user has requested non-interactive auth but
        the token is invalid.
    """




    if self.oauth2_parameters.access_token:
      logger.debug('_Authenticate skipping auth because user explicitly '
                   'supplied an access token.')
      raise AuthPermanentFail('Access token is invalid.')
    if self.oauth2_parameters.refresh_token:
      logger.debug('_Authenticate skipping auth because user explicitly '
                   'supplied a refresh token.')
      raise AuthPermanentFail('Refresh token is invalid.')
    if self.oauth2_parameters.token_uri:
      logger.debug('_Authenticate skipping auth because user explicitly '
                   'supplied a Token URI, for example for service account '
                   'authentication with Compute Engine')
      raise AuthPermanentFail('Token URI did not yield a valid token: ' +
                              self.oauth2_parameters.token_uri)
    if not (
        self.oauth2_parameters.client_id
        and self.oauth2_parameters.client_secret):

      raise AuthPermanentFail(
          'Authorization failed: client_id and client_secret both required')

    logger.debug('_Authenticate requesting auth')
    flow = self.oauth2_parameters.get_flow()
    if self.flags.noauth_local_webserver:
      self.credentials = flow.run_console()
    else:
      success = False
      for port in self.flags.auth_host_port:
        try:
          self.credentials = flow.run_local_server(
              host=self.flags.auth_host_name, port=port)
          success = True
        except socket.error:

          pass
      if not success:
        logger.warning('Cannot run local server, fallback to console')
        self.credentials = flow.run_console()

    self.oauth2_parameters.set_credentials(self.credentials)
    logger.debug('_Authenticate new credentials received')
    return

  def Send(
      self, request_path, payload='', content_type='application/octet-stream',
      timeout=None,
      **kwargs):
    """Sends an RPC and returns the response.

    Args:
      request_path: The path to send the request to, eg /api/appversion/create.
      payload: The body of the request, or None to send an empty request.
      content_type: The Content-Type header to use.
      timeout: timeout in seconds; default None i.e. no timeout.
        (Note: for large requests on OS X, the timeout doesn't work right.) Any
          keyword arguments are converted into query string parameters.
      **kwargs: additional GET parameters

    Returns:
      The response body, as a string.

    Raises:
      AuthPermanentFail: If authorization failed in a permanent way.
      six.moves.urllib_error.HTTPError: On most HTTP errors.
    """

    url = '%s://%s%s' % (self.scheme, self.host, request_path)
    if kwargs:
      url += '?' + urllib_parse.urlencode(sorted(kwargs.items()))
    headers = {}
    if self.extra_headers:
      headers.update(self.extra_headers)



    headers['X-appcfg-api-version'] = '1'

    if payload is not None:
      method = 'POST'
      headers['Content-Type'] = content_type
    else:
      method = 'GET'
    if self.host_override:
      headers['Host'] = self.host_override

    def handle_redirects(response, **unused_kwargs):
      """Handle redirects that match login url pattern as HTTP error 401."""


      if response.status_code == 302:
        loc = response.headers.get('location')
        logger.debug('Got 302 redirect. Location: %s', loc)
        if (loc.startswith('https://www.google.com/accounts/ServiceLogin') or
            re.match(
                r'https://www\.google\.com/a/[a-z0-9.-]+/ServiceLogin', loc)):
          response.status_code = 401
        else:
          raise_http_error(url, response, 'Unexpected redirect to %s' % loc)

    response = None

    auth_errors = rpc_errors = timeout_errors = conflict_errors = 0

    while True:
      try:
        response = self.session.request(
            method, url, payload, headers,
            hooks={'response': [handle_redirects]})
        status = response.status_code
      except (exceptions.RefreshError, ValueError):

        if auth_errors < self.auth_max_errors:
          auth_errors += 1
          self._Authenticate()
          continue

        raise

      if status == 200:
        return response.content

      elif status == 401:
        if auth_errors < self.auth_max_errors:
          auth_errors += 1
          self._Authenticate()
          continue

        logging.info('Too many authentication attempts for url %s', url)
        break

      elif status == 408:
        if timeout_errors < self.timeout_max_errors:
          timeout_errors += 1
          logger.debug(
              'Got timeout error %s of %s. Retrying in %s seconds',
              timeout_errors, self.timeout_max_errors, _TIMEOUT_WAIT_TIME)
          time.sleep(_TIMEOUT_WAIT_TIME)
          continue

        break

      elif status == 409:
        if conflict_errors < self.conflict_max_errors:
          conflict_errors += 1

          wait_time = random.randint(0, 10)
          logger.debug(
              'Got conflict error %s of %s. Retrying in %s seconds.',
              conflict_errors, self.conflict_max_errors, wait_time)
          time.sleep(wait_time)
          continue

        break

      elif 500 <= status < 600:
        if rpc_errors < self.rpc_max_errors:
          rpc_errors += 1

          logger.debug(
              'Retrying. This is attempt %s of %s.',
              rpc_errors, self.rpc_max_errors)
          continue

        break

      else:
        logger.debug('Unexpected results: %s', response)
        raise_http_error(url, response, 'Unexpected HTTP status %s' % status)

    logging.info('Too many retries for url %s', url)
    raise_http_error(url, response, response.content if response else '')
