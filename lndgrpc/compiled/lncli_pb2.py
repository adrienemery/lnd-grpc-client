# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lndgrpc/compiled/lncli.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from lndgrpc.compiled import verrpc_pb2 as lndgrpc_dot_compiled_dot_verrpc__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1clndgrpc/compiled/lncli.proto\x12\x07lnclipb\x1a\x1dlndgrpc/compiled/verrpc.proto\"O\n\x0fVersionResponse\x12\x1e\n\x05lncli\x18\x01 \x01(\x0b\x32\x0f.verrpc.Version\x12\x1c\n\x03lnd\x18\x02 \x01(\x0b\x32\x0f.verrpc.VersionB/Z-github.com/lightningnetwork/lnd/lnrpc/lnclipbb\x06proto3')



_VERSIONRESPONSE = DESCRIPTOR.message_types_by_name['VersionResponse']
VersionResponse = _reflection.GeneratedProtocolMessageType('VersionResponse', (_message.Message,), {
  'DESCRIPTOR' : _VERSIONRESPONSE,
  '__module__' : 'lndgrpc.compiled.lncli_pb2'
  # @@protoc_insertion_point(class_scope:lnclipb.VersionResponse)
  })
_sym_db.RegisterMessage(VersionResponse)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z-github.com/lightningnetwork/lnd/lnrpc/lnclipb'
  _VERSIONRESPONSE._serialized_start=72
  _VERSIONRESPONSE._serialized_end=151
# @@protoc_insertion_point(module_scope)
