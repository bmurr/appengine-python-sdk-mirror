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
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: apphosting/tools/devappserver2/grpc_service.proto
"""Generated protocol buffer code."""
import google
from google.net.proto2.python.public import descriptor as _descriptor
from google.net.proto2.python.public import descriptor_pool as _descriptor_pool
from google.net.proto2.python.public import symbol_database as _symbol_database
from google.net.proto2.python.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n1apphosting/tools/devappserver2/grpc_service.proto\x12\x1e\x61pphosting.tools.devappserver2\"|\n\x07Request\x12\x14\n\x0cservice_name\x18\x02 \x01(\t\x12\x0e\n\x06method\x18\x03 \x01(\t\x12\x0f\n\x07request\x18\x04 \x01(\x0c\x12\x12\n\nrequest_id\x18\x05 \x01(\t\x12&\n\x1etxn_add_task_callback_hostport\x18\x06 \x01(\t\"\xd1\x01\n\x08Response\x12\x10\n\x08response\x18\x01 \x01(\x0c\x12\x11\n\texception\x18\x02 \x01(\x0c\x12K\n\x11\x61pplication_error\x18\x03 \x01(\x0b\x32\x30.apphosting.tools.devappserver2.ApplicationError\x12\x16\n\x0ejava_exception\x18\x04 \x01(\x0c\x12;\n\trpc_error\x18\x05 \x01(\x0b\x32(.apphosting.tools.devappserver2.RpcError\"0\n\x10\x41pplicationError\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0e\n\x06\x64\x65tail\x18\x02 \x01(\t\"\xb7\x02\n\x08RpcError\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0e\n\x06\x64\x65tail\x18\x02 \x01(\t\"\x8c\x02\n\tErrorCode\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x12\n\x0e\x43\x41LL_NOT_FOUND\x10\x01\x12\x0f\n\x0bPARSE_ERROR\x10\x02\x12\x16\n\x12SECURITY_VIOLATION\x10\x03\x12\x0e\n\nOVER_QUOTA\x10\x04\x12\x15\n\x11REQUEST_TOO_LARGE\x10\x05\x12\x17\n\x13\x43\x41PABILITY_DISABLED\x10\x06\x12\x14\n\x10\x46\x45\x41TURE_DISABLED\x10\x07\x12\x0f\n\x0b\x42\x41\x44_REQUEST\x10\x08\x12\x16\n\x12RESPONSE_TOO_LARGE\x10\t\x12\r\n\tCANCELLED\x10\n\x12\x10\n\x0cREPLAY_ERROR\x10\x0b\x12\x15\n\x11\x44\x45\x41\x44LINE_EXCEEDED\x10\x0c\x32p\n\x0b\x43\x61llHandler\x12\x61\n\nHandleCall\x12\'.apphosting.tools.devappserver2.Request\x1a(.apphosting.tools.devappserver2.Response\"\x00\x42\x03\xf8\x02\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.appengine.tools.devappserver2.grpc_service_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\370\002\001'
  _globals['_REQUEST']._serialized_start=85
  _globals['_REQUEST']._serialized_end=209
  _globals['_RESPONSE']._serialized_start=212
  _globals['_RESPONSE']._serialized_end=421
  _globals['_APPLICATIONERROR']._serialized_start=423
  _globals['_APPLICATIONERROR']._serialized_end=471
  _globals['_RPCERROR']._serialized_start=474
  _globals['_RPCERROR']._serialized_end=785
  _globals['_RPCERROR_ERRORCODE']._serialized_start=517
  _globals['_RPCERROR_ERRORCODE']._serialized_end=785
  _globals['_CALLHANDLER']._serialized_start=787
  _globals['_CALLHANDLER']._serialized_end=899
try:
    # THESE ELEMENTS WILL BE DEPRECATED.
    # Please use the generated *_pb2_grpc.py files instead.
    import grpc
    from grpc.beta import implementations as beta_implementations
    from grpc.beta import interfaces as beta_interfaces
    from grpc.framework.common import cardinality
    from grpc.framework.interfaces.face import utilities as face_utilities


    class CallHandlerStub(object):
        """Missing associated documentation comment in .proto file."""

        def __init__(self, channel):
            """Constructor.

            Args:
                channel: A grpc.Channel.
            """
            self.HandleCall = channel.unary_unary(
                    '/apphosting.tools.devappserver2.CallHandler/HandleCall',
                    request_serializer=Request.SerializeToString,
                    response_deserializer=Response.FromString,
                    )


    class CallHandlerServicer(object):
        """Missing associated documentation comment in .proto file."""

        def HandleCall(self, request, context):
            """Handles remote api call over gRPC.
            """
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details('Method not implemented!')
            raise NotImplementedError('Method not implemented!')


    def add_CallHandlerServicer_to_server(servicer, server):
        rpc_method_handlers = {
                'HandleCall': grpc.unary_unary_rpc_method_handler(
                        servicer.HandleCall,
                        request_deserializer=Request.FromString,
                        response_serializer=Response.SerializeToString,
                ),
        }
        generic_handler = grpc.method_handlers_generic_handler(
                'apphosting.tools.devappserver2.CallHandler', rpc_method_handlers)
        server.add_generic_rpc_handlers((generic_handler,))


     # This class is part of an EXPERIMENTAL API.
    class CallHandler(object):
        """Missing associated documentation comment in .proto file."""

        @staticmethod
        def HandleCall(request,
                target,
                options=(),
                channel_credentials=None,
                call_credentials=None,
                insecure=False,
                compression=None,
                wait_for_ready=None,
                timeout=None,
                metadata=None):
            return grpc.experimental.unary_unary(request, target, '/apphosting.tools.devappserver2.CallHandler/HandleCall',
                Request.SerializeToString,
                Response.FromString,
                options, channel_credentials,
                insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


    class BetaCallHandlerServicer(object):
        """The Beta API is deprecated for 0.15.0 and later.

        It is recommended to use the GA API (classes and functions in this
        file not marked beta) for all further purposes. This class was generated
        only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
        """Missing associated documentation comment in .proto file."""
        def HandleCall(self, request, context):
            """Handles remote api call over gRPC.
            """
            context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


    class BetaCallHandlerStub(object):
        """The Beta API is deprecated for 0.15.0 and later.

        It is recommended to use the GA API (classes and functions in this
        file not marked beta) for all further purposes. This class was generated
        only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
        """Missing associated documentation comment in .proto file."""
        def HandleCall(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
            """Handles remote api call over gRPC.
            """
            raise NotImplementedError()
        HandleCall.future = None


    def beta_create_CallHandler_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
        """The Beta API is deprecated for 0.15.0 and later.

        It is recommended to use the GA API (classes and functions in this
        file not marked beta) for all further purposes. This function was
        generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
        request_deserializers = {
            ('apphosting.tools.devappserver2.CallHandler', 'HandleCall'): Request.FromString,
        }
        response_serializers = {
            ('apphosting.tools.devappserver2.CallHandler', 'HandleCall'): Response.SerializeToString,
        }
        method_implementations = {
            ('apphosting.tools.devappserver2.CallHandler', 'HandleCall'): face_utilities.unary_unary_inline(servicer.HandleCall),
        }
        server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
        return beta_implementations.server(method_implementations, options=server_options)


    def beta_create_CallHandler_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
        """The Beta API is deprecated for 0.15.0 and later.

        It is recommended to use the GA API (classes and functions in this
        file not marked beta) for all further purposes. This function was
        generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
        request_serializers = {
            ('apphosting.tools.devappserver2.CallHandler', 'HandleCall'): Request.SerializeToString,
        }
        response_deserializers = {
            ('apphosting.tools.devappserver2.CallHandler', 'HandleCall'): Response.FromString,
        }
        cardinalities = {
            'HandleCall': cardinality.Cardinality.UNARY_UNARY,
        }
        stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
        return beta_implementations.dynamic_stub(channel, 'apphosting.tools.devappserver2.CallHandler', cardinalities, options=stub_options)
except ImportError:
    pass
# @@protoc_insertion_point(module_scope)
