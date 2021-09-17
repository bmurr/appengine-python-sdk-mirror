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
"""API for unit tests to control optional features."""

import __builtin__




def Add(feature):
  if hasattr(__builtin__, '_APPENGINE_FEATURE_FLAGS'):

    assert isinstance(__builtin__._APPENGINE_FEATURE_FLAGS, list)
    assert __builtin__._APPENGINE_FEATURE_FLAGS
    __builtin__._APPENGINE_FEATURE_FLAGS.append(feature)
  else:
    __builtin__._APPENGINE_FEATURE_FLAGS = [feature]


def Remove(feature):
  __builtin__._APPENGINE_FEATURE_FLAGS.remove(feature)




  if not __builtin__._APPENGINE_FEATURE_FLAGS:
    del __builtin__._APPENGINE_FEATURE_FLAGS
