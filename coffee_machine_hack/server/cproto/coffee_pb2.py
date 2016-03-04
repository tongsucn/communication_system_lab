# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: coffee.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='coffee.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x0c\x63offee.proto\"s\n\rCoffeeCommand\x12(\n\x04type\x18\x01 \x01(\x0e\x32\x1a.CoffeeCommand.CommandType\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\x0c\"\'\n\x0b\x43ommandType\x12\r\n\tOPERATION\x10\x00\x12\t\n\x05QUERY\x10\x01\"\xfe\x01\n\x08Response\x12$\n\x04type\x18\x01 \x01(\x0e\x32\x16.Response.ResponseType\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12&\n\x07results\x18\x03 \x01(\x0b\x32\x15.Response.ResultTable\x1aH\n\x0bResultTable\x12\r\n\x05POWER\x18\x01 \x01(\x08\x12\r\n\x05WATER\x18\x02 \x01(\x08\x12\r\n\x05\x42\x45\x41NS\x18\x03 \x01(\x08\x12\x0c\n\x04TRAY\x18\x04 \x01(\x08\"E\n\x0cResponseType\x12\x06\n\x02OK\x10\x00\x12\n\n\x06RESULT\x10\x01\x12\x11\n\rOPERATION_ERR\x10\x02\x12\x0e\n\nFORMAT_ERR\x10\x03\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_COFFEECOMMAND_COMMANDTYPE = _descriptor.EnumDescriptor(
  name='CommandType',
  full_name='CoffeeCommand.CommandType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='OPERATION', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='QUERY', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=92,
  serialized_end=131,
)
_sym_db.RegisterEnumDescriptor(_COFFEECOMMAND_COMMANDTYPE)

_RESPONSE_RESPONSETYPE = _descriptor.EnumDescriptor(
  name='ResponseType',
  full_name='Response.ResponseType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='OK', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RESULT', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OPERATION_ERR', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_ERR', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=319,
  serialized_end=388,
)
_sym_db.RegisterEnumDescriptor(_RESPONSE_RESPONSETYPE)


_COFFEECOMMAND = _descriptor.Descriptor(
  name='CoffeeCommand',
  full_name='CoffeeCommand',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='CoffeeCommand.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='command', full_name='CoffeeCommand.command', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _COFFEECOMMAND_COMMANDTYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=16,
  serialized_end=131,
)


_RESPONSE_RESULTTABLE = _descriptor.Descriptor(
  name='ResultTable',
  full_name='Response.ResultTable',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='POWER', full_name='Response.ResultTable.POWER', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='WATER', full_name='Response.ResultTable.WATER', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='BEANS', full_name='Response.ResultTable.BEANS', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='TRAY', full_name='Response.ResultTable.TRAY', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=245,
  serialized_end=317,
)

_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='Response.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='description', full_name='Response.description', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='results', full_name='Response.results', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_RESPONSE_RESULTTABLE, ],
  enum_types=[
    _RESPONSE_RESPONSETYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=134,
  serialized_end=388,
)

_COFFEECOMMAND.fields_by_name['type'].enum_type = _COFFEECOMMAND_COMMANDTYPE
_COFFEECOMMAND_COMMANDTYPE.containing_type = _COFFEECOMMAND
_RESPONSE_RESULTTABLE.containing_type = _RESPONSE
_RESPONSE.fields_by_name['type'].enum_type = _RESPONSE_RESPONSETYPE
_RESPONSE.fields_by_name['results'].message_type = _RESPONSE_RESULTTABLE
_RESPONSE_RESPONSETYPE.containing_type = _RESPONSE
DESCRIPTOR.message_types_by_name['CoffeeCommand'] = _COFFEECOMMAND
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE

CoffeeCommand = _reflection.GeneratedProtocolMessageType('CoffeeCommand', (_message.Message,), dict(
  DESCRIPTOR = _COFFEECOMMAND,
  __module__ = 'coffee_pb2'
  # @@protoc_insertion_point(class_scope:CoffeeCommand)
  ))
_sym_db.RegisterMessage(CoffeeCommand)

Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), dict(

  ResultTable = _reflection.GeneratedProtocolMessageType('ResultTable', (_message.Message,), dict(
    DESCRIPTOR = _RESPONSE_RESULTTABLE,
    __module__ = 'coffee_pb2'
    # @@protoc_insertion_point(class_scope:Response.ResultTable)
    ))
  ,
  DESCRIPTOR = _RESPONSE,
  __module__ = 'coffee_pb2'
  # @@protoc_insertion_point(class_scope:Response)
  ))
_sym_db.RegisterMessage(Response)
_sym_db.RegisterMessage(Response.ResultTable)


# @@protoc_insertion_point(module_scope)
