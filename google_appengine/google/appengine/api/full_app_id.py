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
"""Get the App Engine app ID from environment.

Not to be confused with `google.appengine.api.app_identity.get_application_id()`
which gets a "display" app ID.
"""


import os
from typing import MutableMapping, Optional, Tuple


OsEnvironLike = Optional[MutableMapping[str, str]]

LEGACY_COMPAT = True






def get(environ: OsEnvironLike = None) -> str:
  """Get the application ID from the environment.

  Args:
    environ: Environment dictionary. Uses os.environ if `None`.

  Returns:
    Default application ID as a string.

  We read from the environment GAE_APPLICATION.
  """

  if environ is None:
    environ = os.environ
  app_id = environ.get('GAE_APPLICATION', '')
  if LEGACY_COMPAT and 'APPLICATION_ID' in environ:
    app_id = environ['APPLICATION_ID']
  return app_id


def put(app_id: str, environ: OsEnvironLike = None) -> None:
  """Set the application ID in the environment.

  Args:
    app_id: Application ID as a string.
    environ: Environment dictionary. Uses os.environ if `None`.
  """

  if environ is None:
    environ = os.environ

  environ['GAE_APPLICATION'] = app_id
  if LEGACY_COMPAT:
    environ['APPLICATION_ID'] = app_id


def normalize(environ: OsEnvironLike = None) -> None:
  """Normalize the environment variables which set the app ID."""

  put(get(environ=environ), environ=environ)


def clear(environ: OsEnvironLike = None) -> None:
  """Unset the application ID in the environment.

  Args:
    environ: Environment dictionary. Uses os.environ if `None`.
  """

  if environ is None:
    environ = os.environ

  environ.pop('GAE_APPLICATION', None)
  if LEGACY_COMPAT:
    environ.pop('APPLICATION_ID', None)


_PARTITION_SEPARATOR = '~'
_DOMAIN_SEPARATOR = ':'


def parse(app_id: Optional[str] = None,
          environ: OsEnvironLike = None) -> Tuple[str, str, str]:
  """Parses a full app ID into `partition`, `domain_name`, and `display_app_id`.

  Args:
    app_id: The full partitioned app ID. Looks up from environ if `None`.
    environ: Environment dictionary. Uses os.environ if `None`.

  Returns:
    A tuple `(partition, domain_name, display_app_id)`.  The partition and
    domain name might be empty.
  """
  if app_id is None:
    app_id = get(environ)
  partition = ''
  psep = app_id.find(_PARTITION_SEPARATOR)
  if psep > 0:
    partition = app_id[:psep]
    app_id = app_id[psep+1:]
  domain_name = ''
  dsep = app_id.find(_DOMAIN_SEPARATOR)
  if dsep > 0:
    domain_name = app_id[:dsep]
    app_id = app_id[dsep+1:]
  return partition, domain_name, app_id


def project_id(app_id: Optional[str] = None,
               environ: OsEnvironLike = None) -> str:
  """Parses the domain prefixed project ID from the app_id.

  Args:
    app_id: The full partitioned app ID. Looks up from environ if `None`.
    environ: Environment dictionary. Uses os.environ if `None`.

  Returns:
    The project id as a string, including the domain if there is one.
  """
  _, domain_name, display_app_id = parse(app_id, environ)
  if domain_name:
    return f'{domain_name}{_DOMAIN_SEPARATOR}{display_app_id}'
  return display_app_id
