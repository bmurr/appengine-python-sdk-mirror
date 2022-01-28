#
# Copyright 2008 The ndb Authors. All Rights Reserved.
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

"""Dynamically decide from where to import Google App Engine modules.

All other NDB code should import its Google App Engine modules from
this module.  If necessary, add new imports here (in both places).
"""
# pylint: disable=unused-import, g-import-not-at-top

import os
import sys

from google.appengine.api import apiproxy_rpc
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_types
from google.appengine.api import memcache
from google.appengine.api import namespace_manager
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.api.blobstore import blobstore as api_blobstore
from google.appengine.datastore import datastore_pbs
from google.appengine.datastore import datastore_query
from google.appengine.datastore import datastore_rpc
from google.appengine.datastore import entity_pb
from google.appengine.ext import db
from google.appengine.ext import gql
from google.appengine.ext.blobstore import blobstore as ext_blobstore
try:
  from google.appengine.runtime import apiproxy as callback
  # Python 2.5 and dev_appserver is not supported.
  if not hasattr(callback, 'SetRequestEndCallback'):
    callback = None
except ImportError:
  callback = None
from google.appengine.runtime import apiproxy_errors
from google.net.proto import ProtocolBuffer

EXTRA_PROTOBUF_DECODE_ERRORS = ()

try:
  # If we have access to the various protobuf implementations shipped with
  # GAE Python 2.7, import all their ProtocolBufferDecodeError variants.
  from google.appengine._internal.proto1 import message as message1
  from google.appengine._internal.proto2 import message as message2
  EXTRA_PROTOBUF_DECODE_ERRORS += (message1.DecodeError, message2.DecodeError)
except ImportError:
  pass
