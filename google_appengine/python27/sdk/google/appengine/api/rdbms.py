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
"""Stub for the old First Generation Cloud SQL API.

This no longer works, but is kept around to prevent ImportErrors.
"""









import logging

logging.warning("Please remove any imports of google.appengine.api.rdbms.  "
                "First Generation Cloud SQL instances have been shut down, and "
                "rdbms.py will be removed in a future release.  See: "
                "https://cloud.google.com/sql/docs/mysql/deprecation-notice")


class Error(StandardError):
  pass


class InterfaceError(Error):
  pass


class DatabaseError(Error):
  pass


class DataError(DatabaseError):
  pass


class OperationalError(DatabaseError):
  pass


class IntegrityError(DatabaseError):
  pass


class InternalError(DatabaseError):
  pass


class ProgrammingError(DatabaseError):
  pass


class NotSupportedError(DatabaseError):
  pass


def set_instance(instance):
  pass


def connect(instance=None, database=None, **kwargs):
  """Fake-connect to Cloud SQL v1."""
  raise OperationalError(
      "could not connect: First Generation Cloud SQL instances have been shut "
      "down.  See: https://cloud.google.com/sql/docs/mysql/deprecation-notice")
