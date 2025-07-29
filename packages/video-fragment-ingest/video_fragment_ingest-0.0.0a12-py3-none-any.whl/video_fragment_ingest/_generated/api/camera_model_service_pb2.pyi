from models import graph_models_pb2 as _graph_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalizationReadyStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[LocalizationReadyStatus]
    ALL: _ClassVar[LocalizationReadyStatus]
    READY: _ClassVar[LocalizationReadyStatus]
    NOT_READY: _ClassVar[LocalizationReadyStatus]
UNKNOWN: LocalizationReadyStatus
ALL: LocalizationReadyStatus
READY: LocalizationReadyStatus
NOT_READY: LocalizationReadyStatus

class GetCameraManufacturersRequest(_message.Message):
    __slots__ = ("predicate",)
    PREDICATE_FIELD_NUMBER: _ClassVar[int]
    predicate: str
    def __init__(self, predicate: _Optional[str] = ...) -> None: ...

class GetCameraManufacturersResponse(_message.Message):
    __slots__ = ("manufacturers",)
    MANUFACTURERS_FIELD_NUMBER: _ClassVar[int]
    manufacturers: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.CameraManufacturer]
    def __init__(self, manufacturers: _Optional[_Iterable[_Union[_graph_models_pb2.CameraManufacturer, _Mapping]]] = ...) -> None: ...

class GetCameraModelsRequest(_message.Message):
    __slots__ = ("manufacturer", "predicate", "localization_ready_status")
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    PREDICATE_FIELD_NUMBER: _ClassVar[int]
    LOCALIZATION_READY_STATUS_FIELD_NUMBER: _ClassVar[int]
    manufacturer: _graph_models_pb2.CameraManufacturer
    predicate: str
    localization_ready_status: LocalizationReadyStatus
    def __init__(self, manufacturer: _Optional[_Union[_graph_models_pb2.CameraManufacturer, _Mapping]] = ..., predicate: _Optional[str] = ..., localization_ready_status: _Optional[_Union[LocalizationReadyStatus, str]] = ...) -> None: ...

class GetCameraModelsResponse(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.CameraModel]
    def __init__(self, models: _Optional[_Iterable[_Union[_graph_models_pb2.CameraModel, _Mapping]]] = ...) -> None: ...
