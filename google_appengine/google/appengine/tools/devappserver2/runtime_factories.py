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
"""One place for all runtime instance factories."""

from google.appengine.tools.devappserver2.go import instance_factory as go_factory
from google.appengine.tools.devappserver2.php import instance_factory as php_factory
from google.appengine.tools.devappserver2.python import instance_factory as python_factory


FACTORIES = {
    'go119': go_factory.GoRuntimeInstanceFactory,
    'go120': go_factory.GoRuntimeInstanceFactory,
    'go121': go_factory.GoRuntimeInstanceFactory,
    'go122': go_factory.GoRuntimeInstanceFactory,
    'php81': php_factory.PHPRuntimeInstanceFactory,
    'php82': php_factory.PHPRuntimeInstanceFactory,
    'python38': python_factory.PythonRuntimeInstanceFactory,
    'python39': python_factory.PythonRuntimeInstanceFactory,
    'python310': python_factory.PythonRuntimeInstanceFactory,
    'python311': python_factory.PythonRuntimeInstanceFactory,
    'python312': python_factory.PythonRuntimeInstanceFactory,
}

# TODO: Remove with references and code for not MODERN_RUNTIMES.
MODERN_RUNTIMES = frozenset(FACTORIES.keys())


def valid_runtimes():
  return list(FACTORIES.keys())
