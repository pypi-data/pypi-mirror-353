from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EntityProtoType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GLOBAL: _ClassVar[EntityProtoType]
    CUSTOMER: _ClassVar[EntityProtoType]
    FACILITY: _ClassVar[EntityProtoType]
    CAMERA: _ClassVar[EntityProtoType]
    OBJECT: _ClassVar[EntityProtoType]
    ZONE: _ClassVar[EntityProtoType]
    BADGE_READER: _ClassVar[EntityProtoType]
    VAPE_DETECTOR: _ClassVar[EntityProtoType]
GLOBAL: EntityProtoType
CUSTOMER: EntityProtoType
FACILITY: EntityProtoType
CAMERA: EntityProtoType
OBJECT: EntityProtoType
ZONE: EntityProtoType
BADGE_READER: EntityProtoType
VAPE_DETECTOR: EntityProtoType

class FeatureKey(_message.Message):
    __slots__ = ("cameraId", "facilityId", "name")
    CAMERAID_FIELD_NUMBER: _ClassVar[int]
    FACILITYID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    cameraId: str
    facilityId: str
    name: str
    def __init__(self, cameraId: _Optional[str] = ..., facilityId: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class EntityProto(_message.Message):
    __slots__ = ("id", "entityType")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENTITYTYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    entityType: EntityProtoType
    def __init__(self, id: _Optional[str] = ..., entityType: _Optional[_Union[EntityProtoType, str]] = ...) -> None: ...

class FeatureProto(_message.Message):
    __slots__ = ("entity", "name", "stringValue", "intValue", "floatValue", "doubleValue", "booleanValue", "longValue", "bytesValue", "timestamp", "cameraId", "facilityId", "zoneId")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STRINGVALUE_FIELD_NUMBER: _ClassVar[int]
    INTVALUE_FIELD_NUMBER: _ClassVar[int]
    FLOATVALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLEVALUE_FIELD_NUMBER: _ClassVar[int]
    BOOLEANVALUE_FIELD_NUMBER: _ClassVar[int]
    LONGVALUE_FIELD_NUMBER: _ClassVar[int]
    BYTESVALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CAMERAID_FIELD_NUMBER: _ClassVar[int]
    FACILITYID_FIELD_NUMBER: _ClassVar[int]
    ZONEID_FIELD_NUMBER: _ClassVar[int]
    entity: EntityProto
    name: str
    stringValue: str
    intValue: int
    floatValue: float
    doubleValue: float
    booleanValue: bool
    longValue: int
    bytesValue: bytes
    timestamp: _timestamp_pb2.Timestamp
    cameraId: str
    facilityId: str
    zoneId: str
    def __init__(self, entity: _Optional[_Union[EntityProto, _Mapping]] = ..., name: _Optional[str] = ..., stringValue: _Optional[str] = ..., intValue: _Optional[int] = ..., floatValue: _Optional[float] = ..., doubleValue: _Optional[float] = ..., booleanValue: bool = ..., longValue: _Optional[int] = ..., bytesValue: _Optional[bytes] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cameraId: _Optional[str] = ..., facilityId: _Optional[str] = ..., zoneId: _Optional[str] = ...) -> None: ...

class FeatureProtoList(_message.Message):
    __slots__ = ("features",)
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    features: _containers.RepeatedCompositeFieldContainer[FeatureProto]
    def __init__(self, features: _Optional[_Iterable[_Union[FeatureProto, _Mapping]]] = ...) -> None: ...
