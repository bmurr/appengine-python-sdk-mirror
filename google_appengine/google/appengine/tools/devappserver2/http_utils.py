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
"""HTTP utils for devappserver."""

import contextlib
import socket
import time

import six.moves.http_client


class Error(Exception):
  """Base class for errors in this module."""


# pylint: disable=g-bad-exception-name
class HostNotReachable(Error):
  """Raised if host can't be reached at given port."""


def wait_for_connection(host, port, process, retries=1):
  """Tries to connect to the given host and port.

  Retries until success, process death, or number of retires is used up.

  Args:
    host: str, Host to connect to.
    port: int, Port to connect to.
    process: subprocess.Popen, the process we are trying to connect to.
    retries: int, Number of connection retries.

  Raises:
      HostNotReachable: if host:port can't be reached after given number of
        retries.
  """

  def ping():
    connection = six.moves.http_client.HTTPConnection(host, port)
    with contextlib.closing(connection):
      try:
        connection.connect()
      except (socket.error, six.moves.http_client.HTTPException):
        return False
      else:
        return True

  while not ping():
    retries -= 1
    if process.poll() is not None or retries <= 0:
      raise HostNotReachable(
          'Cannot connect to the instance on {host}:{port}'.format(
              host=host, port=port))
    time.sleep(1)
