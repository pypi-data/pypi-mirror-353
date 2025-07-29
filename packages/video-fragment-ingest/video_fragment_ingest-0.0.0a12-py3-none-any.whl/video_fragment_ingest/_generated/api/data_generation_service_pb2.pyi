from google.protobuf import empty_pb2 as _empty_pb2
from models import graph_models_pb2 as _graph_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestInferenceFrameStream(_message.Message):
    __slots__ = ("duration", "show_object_at_time", "camera_id", "test_mode")
    class TestMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TEST_CASE: _ClassVar[TestInferenceFrameStream.TestMode]
        WEAPON: _ClassVar[TestInferenceFrameStream.TestMode]
        MEDICAL: _ClassVar[TestInferenceFrameStream.TestMode]
    UNKNOWN_TEST_CASE: TestInferenceFrameStream.TestMode
    WEAPON: TestInferenceFrameStream.TestMode
    MEDICAL: TestInferenceFrameStream.TestMode
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SHOW_OBJECT_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    TEST_MODE_FIELD_NUMBER: _ClassVar[int]
    duration: int
    show_object_at_time: _containers.RepeatedScalarFieldContainer[int]
    camera_id: str
    test_mode: TestInferenceFrameStream.TestMode
    def __init__(self, duration: _Optional[int] = ..., show_object_at_time: _Optional[_Iterable[int]] = ..., camera_id: _Optional[str] = ..., test_mode: _Optional[_Union[TestInferenceFrameStream.TestMode, str]] = ...) -> None: ...

class GenerationRequest(_message.Message):
    __slots__ = ("record_count",)
    RECORD_COUNT_FIELD_NUMBER: _ClassVar[int]
    record_count: int
    def __init__(self, record_count: _Optional[int] = ...) -> None: ...
