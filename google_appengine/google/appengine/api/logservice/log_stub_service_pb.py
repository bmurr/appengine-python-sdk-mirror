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
from google.appengine.api.logservice.log_service_pb import *
import google.appengine.api.logservice.log_service_pb
google_dot_apphosting_dot_api_dot_logservice_dot_log__service__pb = __import__('google.appengine.api.logservice.log_service_pb', {}, {}, [''])
class AddRequestInfoRequest(ProtocolBuffer.ProtocolMessage):
  has_request_log_ = 0
  request_log_ = None

  def __init__(self, contents=None):
    self.lazy_init_lock_ = _Lock()
    if contents is not None: self.MergeFromString(contents)

  def request_log(self):
    if self.request_log_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.request_log_ is None: self.request_log_ = google.appengine.api.logservice.log_service_pb.RequestLog()
      finally:
        self.lazy_init_lock_.release()
    return self.request_log_

  def mutable_request_log(self): self.has_request_log_ = 1; return self.request_log()

  def clear_request_log(self):

    if self.has_request_log_:
      self.has_request_log_ = 0;
      if self.request_log_ is not None: self.request_log_.Clear()

  def has_request_log(self): return self.has_request_log_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_request_log()): self.mutable_request_log().MergeFrom(x.request_log())

  def Equals(self, x):
    if x is self: return 1
    if self.has_request_log_ != x.has_request_log_: return 0
    if self.has_request_log_ and self.request_log_ != x.request_log_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (self.has_request_log_ and not self.request_log_.IsInitialized(debug_strs)): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_request_log_): n += 1 + self.lengthString(self.request_log_.ByteSize())
    return n

  def ByteSizePartial(self):
    n = 0
    if (self.has_request_log_): n += 1 + self.lengthString(self.request_log_.ByteSizePartial())
    return n

  def Clear(self):
    self.clear_request_log()

  def OutputUnchecked(self, out):
    if (self.has_request_log_):
      out.putVarInt32(10)
      out.putVarInt32(self.request_log_.ByteSize())
      self.request_log_.OutputUnchecked(out)

  def OutputPartial(self, out):
    if (self.has_request_log_):
      out.putVarInt32(10)
      out.putVarInt32(self.request_log_.ByteSizePartial())
      self.request_log_.OutputPartial(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_request_log().TryMerge(tmp)
        continue


      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError()
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_request_log_:
      res+=prefix+"request_log <\n"
      res+=self.request_log_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in range(0, 1+maxtag)])

  krequest_log = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "request_log",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)


  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _PROTO_DESCRIPTOR_NAME = 'apphosting.AddRequestInfoRequest'
class AddAppLogLineRequest(ProtocolBuffer.ProtocolMessage):
  has_log_line_ = 0
  log_line_ = None
  has_request_id_ = 0
  request_id_ = ""

  def __init__(self, contents=None):
    self.lazy_init_lock_ = _Lock()
    if contents is not None: self.MergeFromString(contents)

  def log_line(self):
    if self.log_line_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.log_line_ is None: self.log_line_ = google.appengine.api.logservice.log_service_pb.LogLine()
      finally:
        self.lazy_init_lock_.release()
    return self.log_line_

  def mutable_log_line(self): self.has_log_line_ = 1; return self.log_line()

  def clear_log_line(self):

    if self.has_log_line_:
      self.has_log_line_ = 0;
      if self.log_line_ is not None: self.log_line_.Clear()

  def has_log_line(self): return self.has_log_line_

  def request_id(self): return self.request_id_

  def set_request_id(self, x):
    self.has_request_id_ = 1
    self.request_id_ = x

  def clear_request_id(self):
    if self.has_request_id_:
      self.has_request_id_ = 0
      self.request_id_ = ""

  def has_request_id(self): return self.has_request_id_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_log_line()): self.mutable_log_line().MergeFrom(x.log_line())
    if (x.has_request_id()): self.set_request_id(x.request_id())

  def Equals(self, x):
    if x is self: return 1
    if self.has_log_line_ != x.has_log_line_: return 0
    if self.has_log_line_ and self.log_line_ != x.log_line_: return 0
    if self.has_request_id_ != x.has_request_id_: return 0
    if self.has_request_id_ and self.request_id_ != x.request_id_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (self.has_log_line_ and not self.log_line_.IsInitialized(debug_strs)): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_log_line_): n += 1 + self.lengthString(self.log_line_.ByteSize())
    if (self.has_request_id_): n += 1 + self.lengthString(len(self.request_id_))
    return n

  def ByteSizePartial(self):
    n = 0
    if (self.has_log_line_): n += 1 + self.lengthString(self.log_line_.ByteSizePartial())
    if (self.has_request_id_): n += 1 + self.lengthString(len(self.request_id_))
    return n

  def Clear(self):
    self.clear_log_line()
    self.clear_request_id()

  def OutputUnchecked(self, out):
    if (self.has_log_line_):
      out.putVarInt32(10)
      out.putVarInt32(self.log_line_.ByteSize())
      self.log_line_.OutputUnchecked(out)
    if (self.has_request_id_):
      out.putVarInt32(18)
      out.putPrefixedString(self.request_id_)

  def OutputPartial(self, out):
    if (self.has_log_line_):
      out.putVarInt32(10)
      out.putVarInt32(self.log_line_.ByteSizePartial())
      self.log_line_.OutputPartial(out)
    if (self.has_request_id_):
      out.putVarInt32(18)
      out.putPrefixedString(self.request_id_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_log_line().TryMerge(tmp)
        continue
      if tt == 18:
        self.set_request_id(d.getPrefixedString())
        continue


      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError()
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_log_line_:
      res+=prefix+"log_line <\n"
      res+=self.log_line_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    if self.has_request_id_: res+=prefix+("request_id: %s\n" % self.DebugFormatString(self.request_id_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in range(0, 1+maxtag)])

  klog_line = 1
  krequest_id = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "log_line",
    2: "request_id",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)


  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _PROTO_DESCRIPTOR_NAME = 'apphosting.AddAppLogLineRequest'
class StartRequestLogRequest(ProtocolBuffer.ProtocolMessage):
  has_request_id_ = 0
  request_id_ = ""
  has_user_request_id_ = 0
  user_request_id_ = ""
  has_ip_ = 0
  ip_ = ""
  has_app_id_ = 0
  app_id_ = ""
  has_version_id_ = 0
  version_id_ = ""
  has_nickname_ = 0
  nickname_ = ""
  has_user_agent_ = 0
  user_agent_ = ""
  has_host_ = 0
  host_ = ""
  has_method_ = 0
  method_ = ""
  has_resource_ = 0
  resource_ = ""
  has_http_version_ = 0
  http_version_ = ""
  has_start_time_ = 0
  start_time_ = 0
  has_module_ = 0
  module_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def request_id(self): return self.request_id_

  def set_request_id(self, x):
    self.has_request_id_ = 1
    self.request_id_ = x

  def clear_request_id(self):
    if self.has_request_id_:
      self.has_request_id_ = 0
      self.request_id_ = ""

  def has_request_id(self): return self.has_request_id_

  def user_request_id(self): return self.user_request_id_

  def set_user_request_id(self, x):
    self.has_user_request_id_ = 1
    self.user_request_id_ = x

  def clear_user_request_id(self):
    if self.has_user_request_id_:
      self.has_user_request_id_ = 0
      self.user_request_id_ = ""

  def has_user_request_id(self): return self.has_user_request_id_

  def ip(self): return self.ip_

  def set_ip(self, x):
    self.has_ip_ = 1
    self.ip_ = x

  def clear_ip(self):
    if self.has_ip_:
      self.has_ip_ = 0
      self.ip_ = ""

  def has_ip(self): return self.has_ip_

  def app_id(self): return self.app_id_

  def set_app_id(self, x):
    self.has_app_id_ = 1
    self.app_id_ = x

  def clear_app_id(self):
    if self.has_app_id_:
      self.has_app_id_ = 0
      self.app_id_ = ""

  def has_app_id(self): return self.has_app_id_

  def version_id(self): return self.version_id_

  def set_version_id(self, x):
    self.has_version_id_ = 1
    self.version_id_ = x

  def clear_version_id(self):
    if self.has_version_id_:
      self.has_version_id_ = 0
      self.version_id_ = ""

  def has_version_id(self): return self.has_version_id_

  def nickname(self): return self.nickname_

  def set_nickname(self, x):
    self.has_nickname_ = 1
    self.nickname_ = x

  def clear_nickname(self):
    if self.has_nickname_:
      self.has_nickname_ = 0
      self.nickname_ = ""

  def has_nickname(self): return self.has_nickname_

  def user_agent(self): return self.user_agent_

  def set_user_agent(self, x):
    self.has_user_agent_ = 1
    self.user_agent_ = x

  def clear_user_agent(self):
    if self.has_user_agent_:
      self.has_user_agent_ = 0
      self.user_agent_ = ""

  def has_user_agent(self): return self.has_user_agent_

  def host(self): return self.host_

  def set_host(self, x):
    self.has_host_ = 1
    self.host_ = x

  def clear_host(self):
    if self.has_host_:
      self.has_host_ = 0
      self.host_ = ""

  def has_host(self): return self.has_host_

  def method(self): return self.method_

  def set_method(self, x):
    self.has_method_ = 1
    self.method_ = x

  def clear_method(self):
    if self.has_method_:
      self.has_method_ = 0
      self.method_ = ""

  def has_method(self): return self.has_method_

  def resource(self): return self.resource_

  def set_resource(self, x):
    self.has_resource_ = 1
    self.resource_ = x

  def clear_resource(self):
    if self.has_resource_:
      self.has_resource_ = 0
      self.resource_ = ""

  def has_resource(self): return self.has_resource_

  def http_version(self): return self.http_version_

  def set_http_version(self, x):
    self.has_http_version_ = 1
    self.http_version_ = x

  def clear_http_version(self):
    if self.has_http_version_:
      self.has_http_version_ = 0
      self.http_version_ = ""

  def has_http_version(self): return self.has_http_version_

  def start_time(self): return self.start_time_

  def set_start_time(self, x):
    self.has_start_time_ = 1
    self.start_time_ = x

  def clear_start_time(self):
    if self.has_start_time_:
      self.has_start_time_ = 0
      self.start_time_ = 0

  def has_start_time(self): return self.has_start_time_

  def module(self): return self.module_

  def set_module(self, x):
    self.has_module_ = 1
    self.module_ = x

  def clear_module(self):
    if self.has_module_:
      self.has_module_ = 0
      self.module_ = ""

  def has_module(self): return self.has_module_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_request_id()): self.set_request_id(x.request_id())
    if (x.has_user_request_id()): self.set_user_request_id(x.user_request_id())
    if (x.has_ip()): self.set_ip(x.ip())
    if (x.has_app_id()): self.set_app_id(x.app_id())
    if (x.has_version_id()): self.set_version_id(x.version_id())
    if (x.has_nickname()): self.set_nickname(x.nickname())
    if (x.has_user_agent()): self.set_user_agent(x.user_agent())
    if (x.has_host()): self.set_host(x.host())
    if (x.has_method()): self.set_method(x.method())
    if (x.has_resource()): self.set_resource(x.resource())
    if (x.has_http_version()): self.set_http_version(x.http_version())
    if (x.has_start_time()): self.set_start_time(x.start_time())
    if (x.has_module()): self.set_module(x.module())

  def Equals(self, x):
    if x is self: return 1
    if self.has_request_id_ != x.has_request_id_: return 0
    if self.has_request_id_ and self.request_id_ != x.request_id_: return 0
    if self.has_user_request_id_ != x.has_user_request_id_: return 0
    if self.has_user_request_id_ and self.user_request_id_ != x.user_request_id_: return 0
    if self.has_ip_ != x.has_ip_: return 0
    if self.has_ip_ and self.ip_ != x.ip_: return 0
    if self.has_app_id_ != x.has_app_id_: return 0
    if self.has_app_id_ and self.app_id_ != x.app_id_: return 0
    if self.has_version_id_ != x.has_version_id_: return 0
    if self.has_version_id_ and self.version_id_ != x.version_id_: return 0
    if self.has_nickname_ != x.has_nickname_: return 0
    if self.has_nickname_ and self.nickname_ != x.nickname_: return 0
    if self.has_user_agent_ != x.has_user_agent_: return 0
    if self.has_user_agent_ and self.user_agent_ != x.user_agent_: return 0
    if self.has_host_ != x.has_host_: return 0
    if self.has_host_ and self.host_ != x.host_: return 0
    if self.has_method_ != x.has_method_: return 0
    if self.has_method_ and self.method_ != x.method_: return 0
    if self.has_resource_ != x.has_resource_: return 0
    if self.has_resource_ and self.resource_ != x.resource_: return 0
    if self.has_http_version_ != x.has_http_version_: return 0
    if self.has_http_version_ and self.http_version_ != x.http_version_: return 0
    if self.has_start_time_ != x.has_start_time_: return 0
    if self.has_start_time_ and self.start_time_ != x.start_time_: return 0
    if self.has_module_ != x.has_module_: return 0
    if self.has_module_ and self.module_ != x.module_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_request_id_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: request_id not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.request_id_))
    if (self.has_user_request_id_): n += 1 + self.lengthString(len(self.user_request_id_))
    if (self.has_ip_): n += 1 + self.lengthString(len(self.ip_))
    if (self.has_app_id_): n += 1 + self.lengthString(len(self.app_id_))
    if (self.has_version_id_): n += 1 + self.lengthString(len(self.version_id_))
    if (self.has_nickname_): n += 1 + self.lengthString(len(self.nickname_))
    if (self.has_user_agent_): n += 1 + self.lengthString(len(self.user_agent_))
    if (self.has_host_): n += 1 + self.lengthString(len(self.host_))
    if (self.has_method_): n += 1 + self.lengthString(len(self.method_))
    if (self.has_resource_): n += 1 + self.lengthString(len(self.resource_))
    if (self.has_http_version_): n += 1 + self.lengthString(len(self.http_version_))
    if (self.has_start_time_): n += 1 + self.lengthVarInt64(self.start_time_)
    if (self.has_module_): n += 1 + self.lengthString(len(self.module_))
    return n + 1

  def ByteSizePartial(self):
    n = 0
    if (self.has_request_id_):
      n += 1
      n += self.lengthString(len(self.request_id_))
    if (self.has_user_request_id_): n += 1 + self.lengthString(len(self.user_request_id_))
    if (self.has_ip_): n += 1 + self.lengthString(len(self.ip_))
    if (self.has_app_id_): n += 1 + self.lengthString(len(self.app_id_))
    if (self.has_version_id_): n += 1 + self.lengthString(len(self.version_id_))
    if (self.has_nickname_): n += 1 + self.lengthString(len(self.nickname_))
    if (self.has_user_agent_): n += 1 + self.lengthString(len(self.user_agent_))
    if (self.has_host_): n += 1 + self.lengthString(len(self.host_))
    if (self.has_method_): n += 1 + self.lengthString(len(self.method_))
    if (self.has_resource_): n += 1 + self.lengthString(len(self.resource_))
    if (self.has_http_version_): n += 1 + self.lengthString(len(self.http_version_))
    if (self.has_start_time_): n += 1 + self.lengthVarInt64(self.start_time_)
    if (self.has_module_): n += 1 + self.lengthString(len(self.module_))
    return n

  def Clear(self):
    self.clear_request_id()
    self.clear_user_request_id()
    self.clear_ip()
    self.clear_app_id()
    self.clear_version_id()
    self.clear_nickname()
    self.clear_user_agent()
    self.clear_host()
    self.clear_method()
    self.clear_resource()
    self.clear_http_version()
    self.clear_start_time()
    self.clear_module()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.request_id_)
    if (self.has_user_request_id_):
      out.putVarInt32(18)
      out.putPrefixedString(self.user_request_id_)
    if (self.has_ip_):
      out.putVarInt32(26)
      out.putPrefixedString(self.ip_)
    if (self.has_app_id_):
      out.putVarInt32(34)
      out.putPrefixedString(self.app_id_)
    if (self.has_version_id_):
      out.putVarInt32(42)
      out.putPrefixedString(self.version_id_)
    if (self.has_nickname_):
      out.putVarInt32(50)
      out.putPrefixedString(self.nickname_)
    if (self.has_user_agent_):
      out.putVarInt32(58)
      out.putPrefixedString(self.user_agent_)
    if (self.has_host_):
      out.putVarInt32(66)
      out.putPrefixedString(self.host_)
    if (self.has_method_):
      out.putVarInt32(74)
      out.putPrefixedString(self.method_)
    if (self.has_resource_):
      out.putVarInt32(82)
      out.putPrefixedString(self.resource_)
    if (self.has_http_version_):
      out.putVarInt32(90)
      out.putPrefixedString(self.http_version_)
    if (self.has_start_time_):
      out.putVarInt32(96)
      out.putVarInt64(self.start_time_)
    if (self.has_module_):
      out.putVarInt32(106)
      out.putPrefixedString(self.module_)

  def OutputPartial(self, out):
    if (self.has_request_id_):
      out.putVarInt32(10)
      out.putPrefixedString(self.request_id_)
    if (self.has_user_request_id_):
      out.putVarInt32(18)
      out.putPrefixedString(self.user_request_id_)
    if (self.has_ip_):
      out.putVarInt32(26)
      out.putPrefixedString(self.ip_)
    if (self.has_app_id_):
      out.putVarInt32(34)
      out.putPrefixedString(self.app_id_)
    if (self.has_version_id_):
      out.putVarInt32(42)
      out.putPrefixedString(self.version_id_)
    if (self.has_nickname_):
      out.putVarInt32(50)
      out.putPrefixedString(self.nickname_)
    if (self.has_user_agent_):
      out.putVarInt32(58)
      out.putPrefixedString(self.user_agent_)
    if (self.has_host_):
      out.putVarInt32(66)
      out.putPrefixedString(self.host_)
    if (self.has_method_):
      out.putVarInt32(74)
      out.putPrefixedString(self.method_)
    if (self.has_resource_):
      out.putVarInt32(82)
      out.putPrefixedString(self.resource_)
    if (self.has_http_version_):
      out.putVarInt32(90)
      out.putPrefixedString(self.http_version_)
    if (self.has_start_time_):
      out.putVarInt32(96)
      out.putVarInt64(self.start_time_)
    if (self.has_module_):
      out.putVarInt32(106)
      out.putPrefixedString(self.module_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_request_id(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_user_request_id(d.getPrefixedString())
        continue
      if tt == 26:
        self.set_ip(d.getPrefixedString())
        continue
      if tt == 34:
        self.set_app_id(d.getPrefixedString())
        continue
      if tt == 42:
        self.set_version_id(d.getPrefixedString())
        continue
      if tt == 50:
        self.set_nickname(d.getPrefixedString())
        continue
      if tt == 58:
        self.set_user_agent(d.getPrefixedString())
        continue
      if tt == 66:
        self.set_host(d.getPrefixedString())
        continue
      if tt == 74:
        self.set_method(d.getPrefixedString())
        continue
      if tt == 82:
        self.set_resource(d.getPrefixedString())
        continue
      if tt == 90:
        self.set_http_version(d.getPrefixedString())
        continue
      if tt == 96:
        self.set_start_time(d.getVarInt64())
        continue
      if tt == 106:
        self.set_module(d.getPrefixedString())
        continue


      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError()
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_request_id_: res+=prefix+("request_id: %s\n" % self.DebugFormatString(self.request_id_))
    if self.has_user_request_id_: res+=prefix+("user_request_id: %s\n" % self.DebugFormatString(self.user_request_id_))
    if self.has_ip_: res+=prefix+("ip: %s\n" % self.DebugFormatString(self.ip_))
    if self.has_app_id_: res+=prefix+("app_id: %s\n" % self.DebugFormatString(self.app_id_))
    if self.has_version_id_: res+=prefix+("version_id: %s\n" % self.DebugFormatString(self.version_id_))
    if self.has_nickname_: res+=prefix+("nickname: %s\n" % self.DebugFormatString(self.nickname_))
    if self.has_user_agent_: res+=prefix+("user_agent: %s\n" % self.DebugFormatString(self.user_agent_))
    if self.has_host_: res+=prefix+("host: %s\n" % self.DebugFormatString(self.host_))
    if self.has_method_: res+=prefix+("method: %s\n" % self.DebugFormatString(self.method_))
    if self.has_resource_: res+=prefix+("resource: %s\n" % self.DebugFormatString(self.resource_))
    if self.has_http_version_: res+=prefix+("http_version: %s\n" % self.DebugFormatString(self.http_version_))
    if self.has_start_time_: res+=prefix+("start_time: %s\n" % self.DebugFormatInt64(self.start_time_))
    if self.has_module_: res+=prefix+("module: %s\n" % self.DebugFormatString(self.module_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in range(0, 1+maxtag)])

  krequest_id = 1
  kuser_request_id = 2
  kip = 3
  kapp_id = 4
  kversion_id = 5
  knickname = 6
  kuser_agent = 7
  khost = 8
  kmethod = 9
  kresource = 10
  khttp_version = 11
  kstart_time = 12
  kmodule = 13

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "request_id",
    2: "user_request_id",
    3: "ip",
    4: "app_id",
    5: "version_id",
    6: "nickname",
    7: "user_agent",
    8: "host",
    9: "method",
    10: "resource",
    11: "http_version",
    12: "start_time",
    13: "module",
  }, 13)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.STRING,
    4: ProtocolBuffer.Encoder.STRING,
    5: ProtocolBuffer.Encoder.STRING,
    6: ProtocolBuffer.Encoder.STRING,
    7: ProtocolBuffer.Encoder.STRING,
    8: ProtocolBuffer.Encoder.STRING,
    9: ProtocolBuffer.Encoder.STRING,
    10: ProtocolBuffer.Encoder.STRING,
    11: ProtocolBuffer.Encoder.STRING,
    12: ProtocolBuffer.Encoder.NUMERIC,
    13: ProtocolBuffer.Encoder.STRING,
  }, 13, ProtocolBuffer.Encoder.MAX_TYPE)


  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _PROTO_DESCRIPTOR_NAME = 'apphosting.StartRequestLogRequest'
class EndRequestLogRequest(ProtocolBuffer.ProtocolMessage):
  has_request_id_ = 0
  request_id_ = ""
  has_status_ = 0
  status_ = 0
  has_response_size_ = 0
  response_size_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def request_id(self): return self.request_id_

  def set_request_id(self, x):
    self.has_request_id_ = 1
    self.request_id_ = x

  def clear_request_id(self):
    if self.has_request_id_:
      self.has_request_id_ = 0
      self.request_id_ = ""

  def has_request_id(self): return self.has_request_id_

  def status(self): return self.status_

  def set_status(self, x):
    self.has_status_ = 1
    self.status_ = x

  def clear_status(self):
    if self.has_status_:
      self.has_status_ = 0
      self.status_ = 0

  def has_status(self): return self.has_status_

  def response_size(self): return self.response_size_

  def set_response_size(self, x):
    self.has_response_size_ = 1
    self.response_size_ = x

  def clear_response_size(self):
    if self.has_response_size_:
      self.has_response_size_ = 0
      self.response_size_ = 0

  def has_response_size(self): return self.has_response_size_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_request_id()): self.set_request_id(x.request_id())
    if (x.has_status()): self.set_status(x.status())
    if (x.has_response_size()): self.set_response_size(x.response_size())

  def Equals(self, x):
    if x is self: return 1
    if self.has_request_id_ != x.has_request_id_: return 0
    if self.has_request_id_ and self.request_id_ != x.request_id_: return 0
    if self.has_status_ != x.has_status_: return 0
    if self.has_status_ and self.status_ != x.status_: return 0
    if self.has_response_size_ != x.has_response_size_: return 0
    if self.has_response_size_ and self.response_size_ != x.response_size_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_request_id_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: request_id not set.')
    if (not self.has_status_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: status not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.request_id_))
    n += self.lengthVarInt64(self.status_)
    if (self.has_response_size_): n += 1 + self.lengthVarInt64(self.response_size_)
    return n + 2

  def ByteSizePartial(self):
    n = 0
    if (self.has_request_id_):
      n += 1
      n += self.lengthString(len(self.request_id_))
    if (self.has_status_):
      n += 1
      n += self.lengthVarInt64(self.status_)
    if (self.has_response_size_): n += 1 + self.lengthVarInt64(self.response_size_)
    return n

  def Clear(self):
    self.clear_request_id()
    self.clear_status()
    self.clear_response_size()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.request_id_)
    out.putVarInt32(16)
    out.putVarInt32(self.status_)
    if (self.has_response_size_):
      out.putVarInt32(24)
      out.putVarInt32(self.response_size_)

  def OutputPartial(self, out):
    if (self.has_request_id_):
      out.putVarInt32(10)
      out.putPrefixedString(self.request_id_)
    if (self.has_status_):
      out.putVarInt32(16)
      out.putVarInt32(self.status_)
    if (self.has_response_size_):
      out.putVarInt32(24)
      out.putVarInt32(self.response_size_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_request_id(d.getPrefixedString())
        continue
      if tt == 16:
        self.set_status(d.getVarInt32())
        continue
      if tt == 24:
        self.set_response_size(d.getVarInt32())
        continue


      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError()
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_request_id_: res+=prefix+("request_id: %s\n" % self.DebugFormatString(self.request_id_))
    if self.has_status_: res+=prefix+("status: %s\n" % self.DebugFormatInt32(self.status_))
    if self.has_response_size_: res+=prefix+("response_size: %s\n" % self.DebugFormatInt32(self.response_size_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in range(0, 1+maxtag)])

  krequest_id = 1
  kstatus = 2
  kresponse_size = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "request_id",
    2: "status",
    3: "response_size",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)


  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _PROTO_DESCRIPTOR_NAME = 'apphosting.EndRequestLogRequest'



if _extension_runtime:
  pass

__all__ = ['AddRequestInfoRequest','AddAppLogLineRequest','StartRequestLogRequest','EndRequestLogRequest']
