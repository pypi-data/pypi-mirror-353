from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from models import graph_models_pb2 as _graph_models_pb2
from models import spatial_models_pb2 as _spatial_models_pb2
from models import ai_models_pb2 as _ai_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRenderingFramesRequest(_message.Message):
    __slots__ = ("facility", "level", "start_timestamp", "end_timestamp", "start_index", "page_size")
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    START_INDEX_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    facility: _graph_models_pb2.Facility
    level: _graph_models_pb2.Level
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    start_index: int
    page_size: int
    def __init__(self, facility: _Optional[_Union[_graph_models_pb2.Facility, _Mapping]] = ..., level: _Optional[_Union[_graph_models_pb2.Level, _Mapping]] = ..., start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., start_index: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class CalibrateCameraRequest(_message.Message):
    __slots__ = ("camera", "image_resolution_height", "image_resolution_width", "image_coordinates", "world_coordinates")
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_RESOLUTION_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_RESOLUTION_WIDTH_FIELD_NUMBER: _ClassVar[int]
    IMAGE_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    WORLD_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    camera: _graph_models_pb2.Camera
    image_resolution_height: int
    image_resolution_width: int
    image_coordinates: _containers.RepeatedCompositeFieldContainer[_spatial_models_pb2.SpatialCoordinate]
    world_coordinates: _containers.RepeatedCompositeFieldContainer[_spatial_models_pb2.SpatialWorldPoint]
    def __init__(self, camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., image_resolution_height: _Optional[int] = ..., image_resolution_width: _Optional[int] = ..., image_coordinates: _Optional[_Iterable[_Union[_spatial_models_pb2.SpatialCoordinate, _Mapping]]] = ..., world_coordinates: _Optional[_Iterable[_Union[_spatial_models_pb2.SpatialWorldPoint, _Mapping]]] = ...) -> None: ...

class GetRenderingFramesResponse(_message.Message):
    __slots__ = ("rendering_frames",)
    RENDERING_FRAMES_FIELD_NUMBER: _ClassVar[int]
    rendering_frames: _containers.RepeatedCompositeFieldContainer[_spatial_models_pb2.RenderingFrame]
    def __init__(self, rendering_frames: _Optional[_Iterable[_Union[_spatial_models_pb2.RenderingFrame, _Mapping]]] = ...) -> None: ...

class CalibrateByFrameRequest(_message.Message):
    __slots__ = ("camera", "inference_frame", "calibrated_objects")
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_FRAME_FIELD_NUMBER: _ClassVar[int]
    CALIBRATED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    camera: _graph_models_pb2.Camera
    inference_frame: _ai_models_pb2.InferenceFrame
    calibrated_objects: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.DetectedObject]
    def __init__(self, camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., inference_frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ..., calibrated_objects: _Optional[_Iterable[_Union[_ai_models_pb2.DetectedObject, _Mapping]]] = ...) -> None: ...

class CalibrateByFrameResponse(_message.Message):
    __slots__ = ("camera", "initial_error", "final_error", "inference_frame")
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    INITIAL_ERROR_FIELD_NUMBER: _ClassVar[int]
    FINAL_ERROR_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_FRAME_FIELD_NUMBER: _ClassVar[int]
    camera: _graph_models_pb2.Camera
    initial_error: float
    final_error: float
    inference_frame: _ai_models_pb2.InferenceFrame
    def __init__(self, camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., initial_error: _Optional[float] = ..., final_error: _Optional[float] = ..., inference_frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ...) -> None: ...

class DebugPointInFloorPlanRequest(_message.Message):
    __slots__ = ("stream_id", "camera")
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    stream_id: str
    camera: _graph_models_pb2.Camera
    def __init__(self, stream_id: _Optional[str] = ..., camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ...) -> None: ...

class DebugPointInFloorPlan(_message.Message):
    __slots__ = ("stream_id", "image_coordinate")
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_COORDINATE_FIELD_NUMBER: _ClassVar[int]
    stream_id: str
    image_coordinate: _spatial_models_pb2.SpatialCoordinate
    def __init__(self, stream_id: _Optional[str] = ..., image_coordinate: _Optional[_Union[_spatial_models_pb2.SpatialCoordinate, _Mapping]] = ...) -> None: ...
