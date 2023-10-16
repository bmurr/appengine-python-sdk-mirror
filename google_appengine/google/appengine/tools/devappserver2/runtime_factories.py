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


# TODO - b/34669624, automatically get Version of python runtime in prod.
PYTHON27_PROD_VERSION = (2, 7, 12)

MODERN_RUNTIMES = frozenset([
    'python37',
    'python38',
    'python39',
    'python310',
    'python311',
    'python312',
    'go111',
    'go112',
    'go113',
    'go114',
    'go115',
    'go116',
    'go118',
    'go119',
    'go120',
    'go121',
    'php72',
    'php81',
    'php82',
])

FACTORIES = {
    'go': go_factory.GoRuntimeInstanceFactory,
    'go111': go_factory.GoRuntimeInstanceFactory,
    'go112': go_factory.GoRuntimeInstanceFactory,
    'go113': go_factory.GoRuntimeInstanceFactory,
    'go114': go_factory.GoRuntimeInstanceFactory,
    'go115': go_factory.GoRuntimeInstanceFactory,
    'go116': go_factory.GoRuntimeInstanceFactory,
    'go118': go_factory.GoRuntimeInstanceFactory,
    'go119': go_factory.GoRuntimeInstanceFactory,
    'go120': go_factory.GoRuntimeInstanceFactory,
    'go121': go_factory.GoRuntimeInstanceFactory,
    'php55': php_factory.PHPRuntimeInstanceFactory,
    'php72': php_factory.PHPRuntimeInstanceFactory,
    'php81': php_factory.PHPRuntimeInstanceFactory,
    'php82': php_factory.PHPRuntimeInstanceFactory,
    'python': python_factory.PythonRuntimeInstanceFactory,
    'python37': python_factory.PythonRuntimeInstanceFactory,
    'python38': python_factory.PythonRuntimeInstanceFactory,
    'python39': python_factory.PythonRuntimeInstanceFactory,
    'python310': python_factory.PythonRuntimeInstanceFactory,
    'python311': python_factory.PythonRuntimeInstanceFactory,
    'python312': python_factory.PythonRuntimeInstanceFactory,
    'python27': python_factory.PythonRuntimeInstanceFactory,
    'python-compat': python_factory.PythonRuntimeInstanceFactory,
}


def valid_runtimes():
  return list(FACTORIES.keys())
