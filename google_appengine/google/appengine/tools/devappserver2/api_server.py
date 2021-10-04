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
"""Module that picks between the python 2 and 3 versions of api_server.py."""
import os.path
import sys

import google
from google.appengine._internal import six

filename = 'api_server_py2.py' if six.PY2 else 'api_server_py3.py'

api_server_src = os.path.join(os.path.dirname(__file__), filename)

if not os.path.exists(api_server_src):
  # If we are currently located inside a wrapper file, adjust the api_server_src
  # path accordingly.
  api_server_src = os.path.join(
      os.path.dirname(__file__), 'google', 'appengine', 'tools',
      'devappserver2', filename)










# pylint: disable=exec-used
exec(open(api_server_src).read())
