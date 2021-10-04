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
"""Tests for google.appengine.tools.devappserver2.tee."""



import google
import unittest
from google.appengine._internal import six

from google.appengine.tools.devappserver2 import tee


class Counter(object):

  def __init__(self, limit):
    self.__index = 0
    self.__limit = limit

  def readline(self):
    if self.__index < self.__limit:
      self.__index += 1
      return six.b('line%d\n' % self.__index)
    return six.b('')


class TeeTest(unittest.TestCase):

  def test_tee(self):
    output = six.BytesIO()
    tee.Tee._MAX_LINES = 3
    t = tee.Tee(Counter(100), output)
    t.start()
    t.join()
    self.assertEqual(b'line98\nline99\nline100\n', t.get_buf())
    expected = six.b('')
    for i in range(100):
      expected += six.b('line%d\n' % (i + 1))
    self.assertEqual(expected, output.getvalue())


if __name__ == '__main__':
  unittest.main()
