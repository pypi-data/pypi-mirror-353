from google.protobuf import timestamp_pb2 as _timestamp_pb2
from models import graph_models_pb2 as _graph_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelArtifact(_message.Message):
    __slots__ = ("id", "version", "object_detection", "feature_extractor", "tracker")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    TRACKER_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: str
    object_detection: str
    feature_extractor: str
    tracker: str
    def __init__(self, id: _Optional[str] = ..., version: _Optional[str] = ..., object_detection: _Optional[str] = ..., feature_extractor: _Optional[str] = ..., tracker: _Optional[str] = ...) -> None: ...

class DeviceActiveModelRequest(_message.Message):
    __slots__ = ("id", "device_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    device_id: str
    def __init__(self, id: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class DeviceActiveModelResponse(_message.Message):
    __slots__ = ("id", "request_id", "device_id", "active_model_artifacts")
    ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_MODEL_ARTIFACTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    request_id: str
    device_id: str
    active_model_artifacts: ModelArtifact
    def __init__(self, id: _Optional[str] = ..., request_id: _Optional[str] = ..., device_id: _Optional[str] = ..., active_model_artifacts: _Optional[_Union[ModelArtifact, _Mapping]] = ...) -> None: ...

class DeviceModelDeployRequest(_message.Message):
    __slots__ = ("id", "deployment_request_id", "device_id", "model", "configs")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    deployment_request_id: str
    device_id: str
    model: ModelArtifact
    configs: VersionedConfigs
    def __init__(self, id: _Optional[str] = ..., deployment_request_id: _Optional[str] = ..., device_id: _Optional[str] = ..., model: _Optional[_Union[ModelArtifact, _Mapping]] = ..., configs: _Optional[_Union[VersionedConfigs, _Mapping]] = ...) -> None: ...

class DeviceModelDeployResponse(_message.Message):
    __slots__ = ("id", "request_id", "device_id", "delivery_status")
    class DeliveryStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[DeviceModelDeployResponse.DeliveryStatus]
        DEPLOYMENT_INITIATED: _ClassVar[DeviceModelDeployResponse.DeliveryStatus]
        DEPLOYMENT_COMPLETED: _ClassVar[DeviceModelDeployResponse.DeliveryStatus]
        DEPLOYMENT_FAILED: _ClassVar[DeviceModelDeployResponse.DeliveryStatus]
    UNKNOWN: DeviceModelDeployResponse.DeliveryStatus
    DEPLOYMENT_INITIATED: DeviceModelDeployResponse.DeliveryStatus
    DEPLOYMENT_COMPLETED: DeviceModelDeployResponse.DeliveryStatus
    DEPLOYMENT_FAILED: DeviceModelDeployResponse.DeliveryStatus
    ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    request_id: str
    device_id: str
    delivery_status: DeviceModelDeployResponse.DeliveryStatus
    def __init__(self, id: _Optional[str] = ..., request_id: _Optional[str] = ..., device_id: _Optional[str] = ..., delivery_status: _Optional[_Union[DeviceModelDeployResponse.DeliveryStatus, str]] = ...) -> None: ...

class ResponseLatestArtifacts(_message.Message):
    __slots__ = ("id", "configs")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    configs: VersionedConfigs
    def __init__(self, id: _Optional[str] = ..., configs: _Optional[_Union[VersionedConfigs, _Mapping]] = ...) -> None: ...

class VersionedConfigs(_message.Message):
    __slots__ = ("id", "configs_json", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_JSON_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    configs_json: str
    created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., configs_json: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeployModelRequest(_message.Message):
    __slots__ = ("id", "devices", "config")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    id: str
    devices: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Device]
    config: str
    def __init__(self, id: _Optional[str] = ..., devices: _Optional[_Iterable[_Union[_graph_models_pb2.Device, _Mapping]]] = ..., config: _Optional[str] = ...) -> None: ...

class DeployModelResponse(_message.Message):
    __slots__ = ("id", "devices")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    id: str
    devices: _containers.RepeatedCompositeFieldContainer[DeviceModelDeployResponse]
    def __init__(self, id: _Optional[str] = ..., devices: _Optional[_Iterable[_Union[DeviceModelDeployResponse, _Mapping]]] = ...) -> None: ...

class DeviceDeployRequestMap(_message.Message):
    __slots__ = ("device_deploy_message_request", "device_deploy_message_latest_response")
    DEVICE_DEPLOY_MESSAGE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DEVICE_DEPLOY_MESSAGE_LATEST_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    device_deploy_message_request: ModelMessageHistory
    device_deploy_message_latest_response: ModelMessageHistory
    def __init__(self, device_deploy_message_request: _Optional[_Union[ModelMessageHistory, _Mapping]] = ..., device_deploy_message_latest_response: _Optional[_Union[ModelMessageHistory, _Mapping]] = ...) -> None: ...

class HistoricDeviceDeployRequest(_message.Message):
    __slots__ = ("id", "device", "num_of_deploys")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    NUM_OF_DEPLOYS_FIELD_NUMBER: _ClassVar[int]
    id: str
    device: _graph_models_pb2.Device
    num_of_deploys: int
    def __init__(self, id: _Optional[str] = ..., device: _Optional[_Union[_graph_models_pb2.Device, _Mapping]] = ..., num_of_deploys: _Optional[int] = ...) -> None: ...

class HistoricDeviceDeployResponse(_message.Message):
    __slots__ = ("id", "device_deploy_history")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_DEPLOY_HISTORY_FIELD_NUMBER: _ClassVar[int]
    id: str
    device_deploy_history: _containers.RepeatedCompositeFieldContainer[DeviceDeployRequestMap]
    def __init__(self, id: _Optional[str] = ..., device_deploy_history: _Optional[_Iterable[_Union[DeviceDeployRequestMap, _Mapping]]] = ...) -> None: ...

class HistoricConfigsResponse(_message.Message):
    __slots__ = ("id", "configs")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    configs: _containers.RepeatedCompositeFieldContainer[VersionedConfigs]
    def __init__(self, id: _Optional[str] = ..., configs: _Optional[_Iterable[_Union[VersionedConfigs, _Mapping]]] = ...) -> None: ...

class HistoricConfigsRequest(_message.Message):
    __slots__ = ("id", "num_of_configs")
    ID_FIELD_NUMBER: _ClassVar[int]
    NUM_OF_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    num_of_configs: int
    def __init__(self, id: _Optional[str] = ..., num_of_configs: _Optional[int] = ...) -> None: ...

class ModelMessageHistory(_message.Message):
    __slots__ = ("id", "timestamp", "device_model_deploy_request", "device_model_deploy_response", "active_model_request", "active_model_response", "deploy_model_request")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_DEPLOY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_DEPLOY_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_MODEL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_MODEL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    DEPLOY_MODEL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    id: str
    timestamp: _timestamp_pb2.Timestamp
    device_model_deploy_request: DeviceModelDeployRequest
    device_model_deploy_response: DeviceModelDeployResponse
    active_model_request: DeviceActiveModelRequest
    active_model_response: DeviceActiveModelResponse
    deploy_model_request: DeployModelRequest
    def __init__(self, id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., device_model_deploy_request: _Optional[_Union[DeviceModelDeployRequest, _Mapping]] = ..., device_model_deploy_response: _Optional[_Union[DeviceModelDeployResponse, _Mapping]] = ..., active_model_request: _Optional[_Union[DeviceActiveModelRequest, _Mapping]] = ..., active_model_response: _Optional[_Union[DeviceActiveModelResponse, _Mapping]] = ..., deploy_model_request: _Optional[_Union[DeployModelRequest, _Mapping]] = ...) -> None: ...
