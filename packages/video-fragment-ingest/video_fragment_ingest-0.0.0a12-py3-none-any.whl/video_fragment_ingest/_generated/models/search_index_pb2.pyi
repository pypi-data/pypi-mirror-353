from google.protobuf import timestamp_pb2 as _timestamp_pb2
from models import ai_models_pb2 as _ai_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OccupancyCount(_message.Message):
    __slots__ = ("id", "contextId", "count", "timestamp", "cameraId", "locationId", "levelId", "facilityId", "zoneId", "detectedObjects")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXTID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CAMERAID_FIELD_NUMBER: _ClassVar[int]
    LOCATIONID_FIELD_NUMBER: _ClassVar[int]
    LEVELID_FIELD_NUMBER: _ClassVar[int]
    FACILITYID_FIELD_NUMBER: _ClassVar[int]
    ZONEID_FIELD_NUMBER: _ClassVar[int]
    DETECTEDOBJECTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    contextId: str
    count: int
    timestamp: _timestamp_pb2.Timestamp
    cameraId: str
    locationId: str
    levelId: str
    facilityId: str
    zoneId: str
    detectedObjects: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.DetectedObject]
    def __init__(self, id: _Optional[str] = ..., contextId: _Optional[str] = ..., count: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cameraId: _Optional[str] = ..., locationId: _Optional[str] = ..., levelId: _Optional[str] = ..., facilityId: _Optional[str] = ..., zoneId: _Optional[str] = ..., detectedObjects: _Optional[_Iterable[_Union[_ai_models_pb2.DetectedObject, _Mapping]]] = ...) -> None: ...
