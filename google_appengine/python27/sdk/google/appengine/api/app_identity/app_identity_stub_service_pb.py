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



from google.net.proto import ProtocolBuffer
import abc
import array
try:
  from thread import allocate_lock as _Lock
except ImportError:
  from threading import Lock as _Lock

if hasattr(__builtins__, 'xrange'): range = xrange

if hasattr(ProtocolBuffer, 'ExtendableProtocolMessage'):
  _extension_runtime = True
  _ExtendableProtocolMessage = ProtocolBuffer.ExtendableProtocolMessage
else:
  _extension_runtime = False
  _ExtendableProtocolMessage = ProtocolBuffer.ProtocolMessage

from google.appengine.api.api_base_pb import *
import google.appengine.api.api_base_pb
google_dot_apphosting_dot_api_dot_api__base__pb = __import__('google.appengine.api.api_base_pb', {}, {}, [''])
class SetDefaultGcsBucketNameRequest(ProtocolBuffer.ProtocolMessage):
  has_default_gcs_bucket_name_ = 0
  default_gcs_bucket_name_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def default_gcs_bucket_name(self): return self.default_gcs_bucket_name_

  def set_default_gcs_bucket_name(self, x):
    self.has_default_gcs_bucket_name_ = 1
    self.default_gcs_bucket_name_ = x

  def clear_default_gcs_bucket_name(self):
    if self.has_default_gcs_bucket_name_:
      self.has_default_gcs_bucket_name_ = 0
      self.default_gcs_bucket_name_ = ""

  def has_default_gcs_bucket_name(self): return self.has_default_gcs_bucket_name_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_default_gcs_bucket_name()): self.set_default_gcs_bucket_name(x.default_gcs_bucket_name())

  def Equals(self, x):
    if x is self: return 1
    if self.has_default_gcs_bucket_name_ != x.has_default_gcs_bucket_name_: return 0
    if self.has_default_gcs_bucket_name_ and self.default_gcs_bucket_name_ != x.default_gcs_bucket_name_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_default_gcs_bucket_name_): n += 1 + self.lengthString(len(self.default_gcs_bucket_name_))
    return n

  def ByteSizePartial(self):
    n = 0
    if (self.has_default_gcs_bucket_name_): n += 1 + self.lengthString(len(self.default_gcs_bucket_name_))
    return n

  def Clear(self):
    self.clear_default_gcs_bucket_name()

  def OutputUnchecked(self, out):
    if (self.has_default_gcs_bucket_name_):
      out.putVarInt32(10)
      out.putPrefixedString(self.default_gcs_bucket_name_)

  def OutputPartial(self, out):
    if (self.has_default_gcs_bucket_name_):
      out.putVarInt32(10)
      out.putPrefixedString(self.default_gcs_bucket_name_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_default_gcs_bucket_name(d.getPrefixedString())
        continue


      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError()
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_default_gcs_bucket_name_: res+=prefix+("default_gcs_bucket_name: %s\n" % self.DebugFormatString(self.default_gcs_bucket_name_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in range(0, 1+maxtag)])

  kdefault_gcs_bucket_name = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "default_gcs_bucket_name",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)


  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _PROTO_DESCRIPTOR_NAME = 'apphosting.SetDefaultGcsBucketNameRequest'



if _extension_runtime:
  pass

__all__ = ['SetDefaultGcsBucketNameRequest']
