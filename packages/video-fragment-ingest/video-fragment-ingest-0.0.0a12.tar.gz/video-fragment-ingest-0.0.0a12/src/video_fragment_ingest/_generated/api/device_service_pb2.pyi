from google.protobuf import empty_pb2 as _empty_pb2
from models import ai_models_pb2 as _ai_models_pb2
from models import model_deployment_pb2 as _model_deployment_pb2
from models import graph_models_pb2 as _graph_models_pb2
from models import service_models_pb2 as _service_models_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrameList(_message.Message):
    __slots__ = ("id", "frames", "timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    frames: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.InferenceFrame]
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., frames: _Optional[_Iterable[_Union[_ai_models_pb2.InferenceFrame, _Mapping]]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
