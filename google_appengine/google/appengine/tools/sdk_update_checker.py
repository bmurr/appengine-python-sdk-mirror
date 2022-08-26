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
"""Vestigial code that used to check for SDK updates."""

from __future__ import print_function
import logging
import os
import sys

import google

from google.appengine._internal.ruamel import yaml




VERSION_FILE = '../../VERSION'


def GetVersionObject():
  """Gets the version of the SDK by parsing the VERSION file.

  Returns:
    A dict with version information or None if the VERSION file does not exist.
  """
  version_filename = os.path.join(os.path.dirname(google.appengine.__file__),
                                  VERSION_FILE)
  try:
    version_fh = open(version_filename)
  except IOError:
    logging.error('Could not find version file at %s', version_filename)
    return None
  try:
    version = yaml.safe_load(version_fh)
  finally:
    version_fh.close()

  return version


def _VersionList(release):
  """Parse a version string into a list of ints.

  Args:
    release: The 'release' version, e.g. '1.2.4'.
        (Due to YAML parsing this may also be an int or float.)

  Returns:
    A list of ints corresponding to the parts of the version string
    between periods.  Example:
      '1.2.4' -> [1, 2, 4]
      '1.2.3.4' -> [1, 2, 3, 4]

  Raises:
    ValueError if not all the parts are valid integers.
  """
  return [int(part) for part in str(release).split('.')]


class SDKUpdateChecker(object):
  """No-op update checker for the decommissioned standalone App Engine SDK.

  Attributes:
    rpcserver: Unused.
    config: The app's AppInfoExternal.  Needed to determine which api_version
      the app is using.
  """

  def __init__(self,
               rpcserver,
               configs):
    """Create a new SDKUpdateChecker.

    Args:
      rpcserver: The AbstractRpcServer to use.
      configs: A list of yaml objects or a single yaml object that specify the
          configuration of this application.
    """
    if not isinstance(configs, list):
      configs = [configs]
    del rpcserver
    self.runtimes = set(config.runtime for config in configs)
    self.runtime_to_api_version = {}
    for config in configs:
      self.runtime_to_api_version.setdefault(
          config.runtime, set()).add(config.api_version)

  def _ParseVersionFile(self):
    """Parse the local VERSION file.

    Returns:
      A Yaml object or None if the file does not exist.
    """
    return GetVersionObject()

  def CheckSupportedVersion(self):
    """Determines if the app's api_version is supported by the SDK.

    Uses the api_version field from the AppInfoExternal to determine if
    the SDK supports that api_version.

    Raises:
      sys.exit if the api_version is not supported.
    """
    version = self._ParseVersionFile()
    if version is None:
      logging.error('Could not determine if the SDK supports the api_version '
                    'requested in app.yaml.')
      return
    unsupported_api_versions_found = False
    for runtime, api_versions in self.runtime_to_api_version.items():
      supported_api_versions = _GetSupportedApiVersions(version, runtime)
      unsupported_api_versions = sorted(api_versions -
                                        set(supported_api_versions))
      if unsupported_api_versions:
        unsupported_api_versions_found = True
        if len(unsupported_api_versions) == 1:


          logging.error('The requested api_version (%s) is not supported by '
                        'the %s runtime in this release of the SDK. The '
                        'supported api_versions are %s.',
                        unsupported_api_versions[0], runtime,
                        supported_api_versions)
        else:
          logging.error('The requested api_versions (%s) are not supported '
                        'by the %s runtime in this release of the SDK. The '
                        'supported api_versions are %s.',
                        unsupported_api_versions, runtime,
                        supported_api_versions)
    if unsupported_api_versions_found:
      sys.exit(1)

  def CheckForUpdates(self):
    pass

  def AllowedToCheckForUpdates(self, input_fn=None):
    del input_fn
    return False


def _GetSupportedApiVersions(versions, runtime):
  """Returns the runtime-specific or general list of supported runtimes.

  The provided 'versions' dict contains a field called 'api_versions'
  which is the list of default versions supported.  This dict may also
  contain a 'supported_api_versions' dict which lists api_versions by
  runtime.  This function will prefer to return the runtime-specific
  api_versions list, but will default to the general list.

  Args:
    versions: dict of versions from app.yaml or /api/updatecheck server.
    runtime: string of current runtime (e.g. 'go').

  Returns:
    List of supported api_versions (e.g. ['go1']).
  """
  if 'supported_api_versions' in versions:
    return versions['supported_api_versions'].get(
        runtime, versions)['api_versions']
  return versions['api_versions']
