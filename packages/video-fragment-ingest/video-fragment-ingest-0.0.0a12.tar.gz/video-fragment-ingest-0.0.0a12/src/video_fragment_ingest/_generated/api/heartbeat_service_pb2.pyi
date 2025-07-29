from google.protobuf import timestamp_pb2 as _timestamp_pb2
from models import graph_models_pb2 as _graph_models_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from api import core_service_pb2 as _core_service_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CameraStatusRequest(_message.Message):
    __slots__ = ("facility", "cameras")
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    facility: _graph_models_pb2.Facility
    cameras: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Camera]
    def __init__(self, facility: _Optional[_Union[_graph_models_pb2.Facility, _Mapping]] = ..., cameras: _Optional[_Iterable[_Union[_graph_models_pb2.Camera, _Mapping]]] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("cameras",)
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    cameras: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Camera]
    def __init__(self, cameras: _Optional[_Iterable[_Union[_graph_models_pb2.Camera, _Mapping]]] = ...) -> None: ...

class HistoricalCameraListRequest(_message.Message):
    __slots__ = ("facility_id", "from_timestamp", "to_timestamp")
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    facility_id: str
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, facility_id: _Optional[str] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class HistoricalCameraListResponse(_message.Message):
    __slots__ = ("cameras",)
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    cameras: _containers.RepeatedCompositeFieldContainer[CameraStatus]
    def __init__(self, cameras: _Optional[_Iterable[_Union[CameraStatus, _Mapping]]] = ...) -> None: ...

class CameraStatus(_message.Message):
    __slots__ = ("id", "online_count", "offline_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    ONLINE_COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    online_count: int
    offline_count: int
    def __init__(self, id: _Optional[str] = ..., online_count: _Optional[int] = ..., offline_count: _Optional[int] = ...) -> None: ...

class CameraStatusHistogramRequest(_message.Message):
    __slots__ = ("facility_id", "camera_id", "from_timestamp", "to_timestamp")
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    facility_id: str
    camera_id: str
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, facility_id: _Optional[str] = ..., camera_id: _Optional[str] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CameraStatusHistogramResponse(_message.Message):
    __slots__ = ("buckets",)
    class Bucket(_message.Message):
        __slots__ = ("timestamp", "online_count", "offline_count", "online_inference_count", "offline_inference_count", "online_recording_count", "offline_recording_count", "online_streaming_count", "offline_streaming_count")
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        ONLINE_COUNT_FIELD_NUMBER: _ClassVar[int]
        OFFLINE_COUNT_FIELD_NUMBER: _ClassVar[int]
        ONLINE_INFERENCE_COUNT_FIELD_NUMBER: _ClassVar[int]
        OFFLINE_INFERENCE_COUNT_FIELD_NUMBER: _ClassVar[int]
        ONLINE_RECORDING_COUNT_FIELD_NUMBER: _ClassVar[int]
        OFFLINE_RECORDING_COUNT_FIELD_NUMBER: _ClassVar[int]
        ONLINE_STREAMING_COUNT_FIELD_NUMBER: _ClassVar[int]
        OFFLINE_STREAMING_COUNT_FIELD_NUMBER: _ClassVar[int]
        timestamp: _timestamp_pb2.Timestamp
        online_count: int
        offline_count: int
        online_inference_count: int
        offline_inference_count: int
        online_recording_count: int
        offline_recording_count: int
        online_streaming_count: int
        offline_streaming_count: int
        def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., online_count: _Optional[int] = ..., offline_count: _Optional[int] = ..., online_inference_count: _Optional[int] = ..., offline_inference_count: _Optional[int] = ..., online_recording_count: _Optional[int] = ..., offline_recording_count: _Optional[int] = ..., online_streaming_count: _Optional[int] = ..., offline_streaming_count: _Optional[int] = ...) -> None: ...
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    buckets: _containers.RepeatedCompositeFieldContainer[CameraStatusHistogramResponse.Bucket]
    def __init__(self, buckets: _Optional[_Iterable[_Union[CameraStatusHistogramResponse.Bucket, _Mapping]]] = ...) -> None: ...
