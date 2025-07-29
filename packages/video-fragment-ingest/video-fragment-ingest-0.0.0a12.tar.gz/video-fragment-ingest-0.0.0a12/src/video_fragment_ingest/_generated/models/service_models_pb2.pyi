from google.protobuf import timestamp_pb2 as _timestamp_pb2
from models import graph_models_pb2 as _graph_models_pb2
from models import ai_models_pb2 as _ai_models_pb2
from models import model_deployment_pb2 as _model_deployment_pb2
from models import spatial_models_pb2 as _spatial_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnvironmentChange(_message.Message):
    __slots__ = ("facilityId", "cameraId", "timestamp", "zoneId", "scope", "evidences", "badgeReaderId", "systemEventId", "sensorId")
    class ScopeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[EnvironmentChange.ScopeType]
        CAMERA: _ClassVar[EnvironmentChange.ScopeType]
        ZONE: _ClassVar[EnvironmentChange.ScopeType]
        FACILITY: _ClassVar[EnvironmentChange.ScopeType]
        BADGE_READER: _ClassVar[EnvironmentChange.ScopeType]
        VAPE_DETECTOR: _ClassVar[EnvironmentChange.ScopeType]
    UNKNOWN: EnvironmentChange.ScopeType
    CAMERA: EnvironmentChange.ScopeType
    ZONE: EnvironmentChange.ScopeType
    FACILITY: EnvironmentChange.ScopeType
    BADGE_READER: EnvironmentChange.ScopeType
    VAPE_DETECTOR: EnvironmentChange.ScopeType
    FACILITYID_FIELD_NUMBER: _ClassVar[int]
    CAMERAID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ZONEID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    EVIDENCES_FIELD_NUMBER: _ClassVar[int]
    BADGEREADERID_FIELD_NUMBER: _ClassVar[int]
    SYSTEMEVENTID_FIELD_NUMBER: _ClassVar[int]
    SENSORID_FIELD_NUMBER: _ClassVar[int]
    facilityId: str
    cameraId: str
    timestamp: _timestamp_pb2.Timestamp
    zoneId: str
    scope: EnvironmentChange.ScopeType
    evidences: _containers.RepeatedScalarFieldContainer[str]
    badgeReaderId: str
    systemEventId: str
    sensorId: str
    def __init__(self, facilityId: _Optional[str] = ..., cameraId: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., zoneId: _Optional[str] = ..., scope: _Optional[_Union[EnvironmentChange.ScopeType, str]] = ..., evidences: _Optional[_Iterable[str]] = ..., badgeReaderId: _Optional[str] = ..., systemEventId: _Optional[str] = ..., sensorId: _Optional[str] = ...) -> None: ...

class CameraIdentifier(_message.Message):
    __slots__ = ("cameraId", "facilityId", "customerId")
    CAMERAID_FIELD_NUMBER: _ClassVar[int]
    FACILITYID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMERID_FIELD_NUMBER: _ClassVar[int]
    cameraId: str
    facilityId: str
    customerId: str
    def __init__(self, cameraId: _Optional[str] = ..., facilityId: _Optional[str] = ..., customerId: _Optional[str] = ...) -> None: ...

class CameraIdentifierList(_message.Message):
    __slots__ = ("cameras",)
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    cameras: _containers.RepeatedCompositeFieldContainer[CameraIdentifier]
    def __init__(self, cameras: _Optional[_Iterable[_Union[CameraIdentifier, _Mapping]]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("channels",)
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, channels: _Optional[_Iterable[str]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("channel", "timestamp", "description", "media_request", "add_camera", "update_camera", "delete_camera", "incident", "device_heartbeat", "camera_heartbeat", "sub_request", "media_response", "pair_camera_request", "pairing_mode", "event", "testing_request", "heartbeat", "notification", "audio_request", "restart_live_view", "floor_plan_completed", "start_kvs_stream", "stop_kvs_stream", "kvs_video_upload", "upload_thumbnail_request", "ffprobe_request", "ffprobe_response", "frame_with_object", "start_video_playback", "web_rtc_heartbeat", "start_live_view", "frame", "upload_manifest", "upload_video_segment", "active_device_model_request", "active_device_model_response", "device_model_deploy_request", "device_model_deploy_response", "match_prediction", "rendering_frame", "facility_control", "restart_device", "system_event")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MEDIA_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ADD_CAMERA_FIELD_NUMBER: _ClassVar[int]
    UPDATE_CAMERA_FIELD_NUMBER: _ClassVar[int]
    DELETE_CAMERA_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    CAMERA_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    SUB_REQUEST_FIELD_NUMBER: _ClassVar[int]
    MEDIA_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    PAIR_CAMERA_REQUEST_FIELD_NUMBER: _ClassVar[int]
    PAIRING_MODE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    TESTING_REQUEST_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    AUDIO_REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESTART_LIVE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FLOOR_PLAN_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    START_KVS_STREAM_FIELD_NUMBER: _ClassVar[int]
    STOP_KVS_STREAM_FIELD_NUMBER: _ClassVar[int]
    KVS_VIDEO_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_THUMBNAIL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    FFPROBE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    FFPROBE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    FRAME_WITH_OBJECT_FIELD_NUMBER: _ClassVar[int]
    START_VIDEO_PLAYBACK_FIELD_NUMBER: _ClassVar[int]
    WEB_RTC_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    START_LIVE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_MANIFEST_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_VIDEO_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DEVICE_MODEL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DEVICE_MODEL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_DEPLOY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_DEPLOY_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MATCH_PREDICTION_FIELD_NUMBER: _ClassVar[int]
    RENDERING_FRAME_FIELD_NUMBER: _ClassVar[int]
    FACILITY_CONTROL_FIELD_NUMBER: _ClassVar[int]
    RESTART_DEVICE_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_EVENT_FIELD_NUMBER: _ClassVar[int]
    channel: str
    timestamp: _timestamp_pb2.Timestamp
    description: str
    media_request: UploadMediaRequest
    add_camera: _graph_models_pb2.Camera
    update_camera: _graph_models_pb2.Camera
    delete_camera: _graph_models_pb2.Camera
    incident: _graph_models_pb2.Incident
    device_heartbeat: _graph_models_pb2.Device
    camera_heartbeat: _graph_models_pb2.Camera
    sub_request: SubscribeRequest
    media_response: UploadMediaResponse
    pair_camera_request: PairCameraRequest
    pairing_mode: bool
    event: _graph_models_pb2.IncidentEvent
    testing_request: TestingRequest
    heartbeat: Heartbeat
    notification: WebNotification
    audio_request: PlayAudioRequest
    restart_live_view: _graph_models_pb2.Camera
    floor_plan_completed: _graph_models_pb2.FloorPlan
    start_kvs_stream: StartKvsStreamRequest
    stop_kvs_stream: StopKvsStreamRequest
    kvs_video_upload: KvsVideoUploadRequest
    upload_thumbnail_request: UploadThumbnailRequest
    ffprobe_request: FFProbRequest
    ffprobe_response: FFProbResponse
    frame_with_object: _graph_models_pb2.Camera
    start_video_playback: StartVideoPlaybackRequest
    web_rtc_heartbeat: WebRTCHeartbeatRequest
    start_live_view: _graph_models_pb2.Camera
    frame: _ai_models_pb2.InferenceFrame
    upload_manifest: ManifestRequest
    upload_video_segment: VideoSegmentRequest
    active_device_model_request: _model_deployment_pb2.DeviceActiveModelRequest
    active_device_model_response: _model_deployment_pb2.DeviceActiveModelResponse
    device_model_deploy_request: _model_deployment_pb2.DeviceModelDeployRequest
    device_model_deploy_response: _model_deployment_pb2.DeviceModelDeployResponse
    match_prediction: _graph_models_pb2.MatchPrediction
    rendering_frame: _spatial_models_pb2.RenderingFrame
    facility_control: _graph_models_pb2.FacilityControl
    restart_device: _graph_models_pb2.Device
    system_event: _graph_models_pb2.SystemEvent
    def __init__(self, channel: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., description: _Optional[str] = ..., media_request: _Optional[_Union[UploadMediaRequest, _Mapping]] = ..., add_camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., update_camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., delete_camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., incident: _Optional[_Union[_graph_models_pb2.Incident, _Mapping]] = ..., device_heartbeat: _Optional[_Union[_graph_models_pb2.Device, _Mapping]] = ..., camera_heartbeat: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., sub_request: _Optional[_Union[SubscribeRequest, _Mapping]] = ..., media_response: _Optional[_Union[UploadMediaResponse, _Mapping]] = ..., pair_camera_request: _Optional[_Union[PairCameraRequest, _Mapping]] = ..., pairing_mode: bool = ..., event: _Optional[_Union[_graph_models_pb2.IncidentEvent, _Mapping]] = ..., testing_request: _Optional[_Union[TestingRequest, _Mapping]] = ..., heartbeat: _Optional[_Union[Heartbeat, _Mapping]] = ..., notification: _Optional[_Union[WebNotification, _Mapping]] = ..., audio_request: _Optional[_Union[PlayAudioRequest, _Mapping]] = ..., restart_live_view: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., floor_plan_completed: _Optional[_Union[_graph_models_pb2.FloorPlan, _Mapping]] = ..., start_kvs_stream: _Optional[_Union[StartKvsStreamRequest, _Mapping]] = ..., stop_kvs_stream: _Optional[_Union[StopKvsStreamRequest, _Mapping]] = ..., kvs_video_upload: _Optional[_Union[KvsVideoUploadRequest, _Mapping]] = ..., upload_thumbnail_request: _Optional[_Union[UploadThumbnailRequest, _Mapping]] = ..., ffprobe_request: _Optional[_Union[FFProbRequest, _Mapping]] = ..., ffprobe_response: _Optional[_Union[FFProbResponse, _Mapping]] = ..., frame_with_object: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., start_video_playback: _Optional[_Union[StartVideoPlaybackRequest, _Mapping]] = ..., web_rtc_heartbeat: _Optional[_Union[WebRTCHeartbeatRequest, _Mapping]] = ..., start_live_view: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ..., upload_manifest: _Optional[_Union[ManifestRequest, _Mapping]] = ..., upload_video_segment: _Optional[_Union[VideoSegmentRequest, _Mapping]] = ..., active_device_model_request: _Optional[_Union[_model_deployment_pb2.DeviceActiveModelRequest, _Mapping]] = ..., active_device_model_response: _Optional[_Union[_model_deployment_pb2.DeviceActiveModelResponse, _Mapping]] = ..., device_model_deploy_request: _Optional[_Union[_model_deployment_pb2.DeviceModelDeployRequest, _Mapping]] = ..., device_model_deploy_response: _Optional[_Union[_model_deployment_pb2.DeviceModelDeployResponse, _Mapping]] = ..., match_prediction: _Optional[_Union[_graph_models_pb2.MatchPrediction, _Mapping]] = ..., rendering_frame: _Optional[_Union[_spatial_models_pb2.RenderingFrame, _Mapping]] = ..., facility_control: _Optional[_Union[_graph_models_pb2.FacilityControl, _Mapping]] = ..., restart_device: _Optional[_Union[_graph_models_pb2.Device, _Mapping]] = ..., system_event: _Optional[_Union[_graph_models_pb2.SystemEvent, _Mapping]] = ...) -> None: ...

class ManifestRequest(_message.Message):
    __slots__ = ("camera_id",)
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    def __init__(self, camera_id: _Optional[str] = ...) -> None: ...

class VideoSegmentRequest(_message.Message):
    __slots__ = ("camera_id", "manifest_timestamp", "segment_filename")
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    MANIFEST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_FILENAME_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    manifest_timestamp: str
    segment_filename: str
    def __init__(self, camera_id: _Optional[str] = ..., manifest_timestamp: _Optional[str] = ..., segment_filename: _Optional[str] = ...) -> None: ...

class WebRTCHeartbeatRequest(_message.Message):
    __slots__ = ("stream_name",)
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    stream_name: str
    def __init__(self, stream_name: _Optional[str] = ...) -> None: ...

class UploadThumbnailRequest(_message.Message):
    __slots__ = ("id", "camera_id", "elapse_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    ELAPSE_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    elapse_time: float
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., elapse_time: _Optional[float] = ...) -> None: ...

class KvsVideoUploadRequest(_message.Message):
    __slots__ = ("id", "camera_id", "start_time", "stop_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    STOP_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    start_time: _timestamp_pb2.Timestamp
    stop_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., stop_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class StartKvsStreamRequest(_message.Message):
    __slots__ = ("camera_id", "frame")
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    frame: _ai_models_pb2.InferenceFrame
    def __init__(self, camera_id: _Optional[str] = ..., frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ...) -> None: ...

class StopKvsStreamRequest(_message.Message):
    __slots__ = ("camera_id",)
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    def __init__(self, camera_id: _Optional[str] = ...) -> None: ...

class StartVideoPlaybackRequest(_message.Message):
    __slots__ = ("camera_id", "stream_name", "start_time", "codec")
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    CODEC_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    stream_name: str
    start_time: _timestamp_pb2.Timestamp
    codec: str
    def __init__(self, camera_id: _Optional[str] = ..., stream_name: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., codec: _Optional[str] = ...) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = ("timestamp", "id", "device")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    id: str
    device: _graph_models_pb2.Device
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., id: _Optional[str] = ..., device: _Optional[_Union[_graph_models_pb2.Device, _Mapping]] = ...) -> None: ...

class TestingRequest(_message.Message):
    __slots__ = ("testing_type", "camera_id", "frame_count")
    class TestingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[TestingRequest.TestingType]
        PERSON: _ClassVar[TestingRequest.TestingType]
        GUN: _ClassVar[TestingRequest.TestingType]
        LONG_GUN: _ClassVar[TestingRequest.TestingType]
        MAN_DOWN: _ClassVar[TestingRequest.TestingType]
    UNKNOWN: TestingRequest.TestingType
    PERSON: TestingRequest.TestingType
    GUN: TestingRequest.TestingType
    LONG_GUN: TestingRequest.TestingType
    MAN_DOWN: TestingRequest.TestingType
    TESTING_TYPE_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_COUNT_FIELD_NUMBER: _ClassVar[int]
    testing_type: TestingRequest.TestingType
    camera_id: str
    frame_count: int
    def __init__(self, testing_type: _Optional[_Union[TestingRequest.TestingType, str]] = ..., camera_id: _Optional[str] = ..., frame_count: _Optional[int] = ...) -> None: ...

class RemoveCameraLocationRequest(_message.Message):
    __slots__ = ("location", "camera", "campus")
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_FIELD_NUMBER: _ClassVar[int]
    location: _graph_models_pb2.Location
    camera: _graph_models_pb2.Camera
    campus: _graph_models_pb2.Campus
    def __init__(self, location: _Optional[_Union[_graph_models_pb2.Location, _Mapping]] = ..., camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., campus: _Optional[_Union[_graph_models_pb2.Campus, _Mapping]] = ...) -> None: ...

class PairCameraRequest(_message.Message):
    __slots__ = ("conf_camera", "pos_camera")
    CONF_CAMERA_FIELD_NUMBER: _ClassVar[int]
    POS_CAMERA_FIELD_NUMBER: _ClassVar[int]
    conf_camera: _graph_models_pb2.Camera
    pos_camera: _graph_models_pb2.Camera
    def __init__(self, conf_camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., pos_camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ...) -> None: ...

class PairMultiLensCameraRequest(_message.Message):
    __slots__ = ("conf_camera", "pos_camera")
    CONF_CAMERA_FIELD_NUMBER: _ClassVar[int]
    POS_CAMERA_FIELD_NUMBER: _ClassVar[int]
    conf_camera: _graph_models_pb2.MultiLensCamera
    pos_camera: _graph_models_pb2.MultiLensCamera
    def __init__(self, conf_camera: _Optional[_Union[_graph_models_pb2.MultiLensCamera, _Mapping]] = ..., pos_camera: _Optional[_Union[_graph_models_pb2.MultiLensCamera, _Mapping]] = ...) -> None: ...

class Authentication(_message.Message):
    __slots__ = ("id_token", "access_token")
    ID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    id_token: str
    access_token: str
    def __init__(self, id_token: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class UserLogin(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class VideoPlayback(_message.Message):
    __slots__ = ("camera_id", "start_time", "end_time")
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    def __init__(self, camera_id: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PresignedUrl(_message.Message):
    __slots__ = ("url", "expires")
    URL_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_FIELD_NUMBER: _ClassVar[int]
    url: str
    expires: _timestamp_pb2.Timestamp
    def __init__(self, url: _Optional[str] = ..., expires: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UploadMediaRequest(_message.Message):
    __slots__ = ("id", "event_id", "camera_id", "frame_ids", "bucket", "key", "type", "start_timestamp", "end_timestamp")
    class MediaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[UploadMediaRequest.MediaType]
        VIDEO: _ClassVar[UploadMediaRequest.MediaType]
        IMAGE: _ClassVar[UploadMediaRequest.MediaType]
        BOTH: _ClassVar[UploadMediaRequest.MediaType]
    UNKNOWN: UploadMediaRequest.MediaType
    VIDEO: UploadMediaRequest.MediaType
    IMAGE: UploadMediaRequest.MediaType
    BOTH: UploadMediaRequest.MediaType
    ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_IDS_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    event_id: str
    camera_id: str
    frame_ids: _containers.RepeatedScalarFieldContainer[str]
    bucket: str
    key: str
    type: UploadMediaRequest.MediaType
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., event_id: _Optional[str] = ..., camera_id: _Optional[str] = ..., frame_ids: _Optional[_Iterable[str]] = ..., bucket: _Optional[str] = ..., key: _Optional[str] = ..., type: _Optional[_Union[UploadMediaRequest.MediaType, str]] = ..., start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UploadMediaResponse(_message.Message):
    __slots__ = ("id", "event_id", "chunks", "request_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    event_id: str
    chunks: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.MediaChunk]
    request_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., event_id: _Optional[str] = ..., chunks: _Optional[_Iterable[_Union[_graph_models_pb2.MediaChunk, _Mapping]]] = ..., request_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PlayAudioRequest(_message.Message):
    __slots__ = ("speaker", "audio")
    SPEAKER_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    speaker: _graph_models_pb2.Speaker
    audio: _graph_models_pb2.SpeechAudio
    def __init__(self, speaker: _Optional[_Union[_graph_models_pb2.Speaker, _Mapping]] = ..., audio: _Optional[_Union[_graph_models_pb2.SpeechAudio, _Mapping]] = ...) -> None: ...

class KVSStream(_message.Message):
    __slots__ = ("camera_id", "customer_id", "facility_id")
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    camera_id: str
    customer_id: str
    facility_id: str
    def __init__(self, camera_id: _Optional[str] = ..., customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ...) -> None: ...

class CloudStreamTask(_message.Message):
    __slots__ = ("add_stream", "remove_stream")
    ADD_STREAM_FIELD_NUMBER: _ClassVar[int]
    REMOVE_STREAM_FIELD_NUMBER: _ClassVar[int]
    add_stream: KVSStream
    remove_stream: KVSStream
    def __init__(self, add_stream: _Optional[_Union[KVSStream, _Mapping]] = ..., remove_stream: _Optional[_Union[KVSStream, _Mapping]] = ...) -> None: ...

class CloudStats(_message.Message):
    __slots__ = ("id", "utilization", "runing_streams")
    ID_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    RUNING_STREAMS_FIELD_NUMBER: _ClassVar[int]
    id: str
    utilization: float
    runing_streams: _containers.RepeatedCompositeFieldContainer[KVSStream]
    def __init__(self, id: _Optional[str] = ..., utilization: _Optional[float] = ..., runing_streams: _Optional[_Iterable[_Union[KVSStream, _Mapping]]] = ...) -> None: ...

class TwilioToken(_message.Message):
    __slots__ = ("conversation_id", "jwt")
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    JWT_FIELD_NUMBER: _ClassVar[int]
    conversation_id: str
    jwt: str
    def __init__(self, conversation_id: _Optional[str] = ..., jwt: _Optional[str] = ...) -> None: ...

class TwilioChannel(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class TwilioMessage(_message.Message):
    __slots__ = ("phone", "content")
    PHONE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    phone: str
    content: str
    def __init__(self, phone: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class TwilioParticipant(_message.Message):
    __slots__ = ("conversation_id", "phone")
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    conversation_id: str
    phone: str
    def __init__(self, conversation_id: _Optional[str] = ..., phone: _Optional[str] = ...) -> None: ...

class TwilioConversationMessage(_message.Message):
    __slots__ = ("incident_id", "conversation_id", "sender", "content", "contact_id")
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTACT_ID_FIELD_NUMBER: _ClassVar[int]
    incident_id: str
    conversation_id: str
    sender: str
    content: str
    contact_id: str
    def __init__(self, incident_id: _Optional[str] = ..., conversation_id: _Optional[str] = ..., sender: _Optional[str] = ..., content: _Optional[str] = ..., contact_id: _Optional[str] = ...) -> None: ...

class WebNotification(_message.Message):
    __slots__ = ("title", "message", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[WebNotification.Type]
        SUCCESS: _ClassVar[WebNotification.Type]
        WARNING: _ClassVar[WebNotification.Type]
        INFO: _ClassVar[WebNotification.Type]
        ERROR: _ClassVar[WebNotification.Type]
    UNKNOWN: WebNotification.Type
    SUCCESS: WebNotification.Type
    WARNING: WebNotification.Type
    INFO: WebNotification.Type
    ERROR: WebNotification.Type
    TITLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    title: str
    message: str
    type: WebNotification.Type
    def __init__(self, title: _Optional[str] = ..., message: _Optional[str] = ..., type: _Optional[_Union[WebNotification.Type, str]] = ...) -> None: ...

class TrailLogRequest(_message.Message):
    __slots__ = ("start_index", "size", "asc", "customer_id", "actions", "resources", "detail", "user_id", "from_timestamp", "to_timestamp")
    START_INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ASC_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    start_index: int
    size: int
    asc: bool
    customer_id: str
    actions: _containers.RepeatedScalarFieldContainer[str]
    resources: _containers.RepeatedScalarFieldContainer[str]
    detail: str
    user_id: str
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, start_index: _Optional[int] = ..., size: _Optional[int] = ..., asc: bool = ..., customer_id: _Optional[str] = ..., actions: _Optional[_Iterable[str]] = ..., resources: _Optional[_Iterable[str]] = ..., detail: _Optional[str] = ..., user_id: _Optional[str] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TrailLogFieldRequest(_message.Message):
    __slots__ = ("customer", "user")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    customer: _graph_models_pb2.Customer
    user: _graph_models_pb2.User
    def __init__(self, customer: _Optional[_Union[_graph_models_pb2.Customer, _Mapping]] = ..., user: _Optional[_Union[_graph_models_pb2.User, _Mapping]] = ...) -> None: ...

class TrailLog(_message.Message):
    __slots__ = ("id", "user", "customer", "action", "resource_name", "details", "facility", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    user: _graph_models_pb2.User
    customer: _graph_models_pb2.Customer
    action: str
    resource_name: str
    details: str
    facility: _graph_models_pb2.Facility
    created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., user: _Optional[_Union[_graph_models_pb2.User, _Mapping]] = ..., customer: _Optional[_Union[_graph_models_pb2.Customer, _Mapping]] = ..., action: _Optional[str] = ..., resource_name: _Optional[str] = ..., details: _Optional[str] = ..., facility: _Optional[_Union[_graph_models_pb2.Facility, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TrailLogField(_message.Message):
    __slots__ = ("customer_id", "actions", "resources")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    actions: _containers.RepeatedScalarFieldContainer[str]
    resources: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_id: _Optional[str] = ..., actions: _Optional[_Iterable[str]] = ..., resources: _Optional[_Iterable[str]] = ...) -> None: ...

class TrailLogList(_message.Message):
    __slots__ = ("logs",)
    LOGS_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[TrailLog]
    def __init__(self, logs: _Optional[_Iterable[_Union[TrailLog, _Mapping]]] = ...) -> None: ...

class CloudVideoDecodingIdentifier(_message.Message):
    __slots__ = ("id", "camera_id", "facility_id", "customer_id", "start_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    facility_id: str
    customer_id: str
    start_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., customer_id: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CameraWithRelationships(_message.Message):
    __slots__ = ("camera", "zone_id", "level_id", "campus_id")
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    ZONE_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_ID_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_ID_FIELD_NUMBER: _ClassVar[int]
    camera: _graph_models_pb2.Camera
    zone_id: str
    level_id: str
    campus_id: str
    def __init__(self, camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., zone_id: _Optional[str] = ..., level_id: _Optional[str] = ..., campus_id: _Optional[str] = ...) -> None: ...

class BadgeReaderWithRelationships(_message.Message):
    __slots__ = ("badge_reader", "zone_id", "level_id", "campus_id")
    BADGE_READER_FIELD_NUMBER: _ClassVar[int]
    ZONE_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_ID_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_ID_FIELD_NUMBER: _ClassVar[int]
    badge_reader: _graph_models_pb2.BadgeReader
    zone_id: str
    level_id: str
    campus_id: str
    def __init__(self, badge_reader: _Optional[_Union[_graph_models_pb2.BadgeReader, _Mapping]] = ..., zone_id: _Optional[str] = ..., level_id: _Optional[str] = ..., campus_id: _Optional[str] = ...) -> None: ...

class FacilityObjectWithRelationships(_message.Message):
    __slots__ = ("zone_id", "level_id", "campus_id", "badge_reader", "vape_detector")
    ZONE_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_ID_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_ID_FIELD_NUMBER: _ClassVar[int]
    BADGE_READER_FIELD_NUMBER: _ClassVar[int]
    VAPE_DETECTOR_FIELD_NUMBER: _ClassVar[int]
    zone_id: str
    level_id: str
    campus_id: str
    badge_reader: _graph_models_pb2.BadgeReader
    vape_detector: _graph_models_pb2.VapeDetector
    def __init__(self, zone_id: _Optional[str] = ..., level_id: _Optional[str] = ..., campus_id: _Optional[str] = ..., badge_reader: _Optional[_Union[_graph_models_pb2.BadgeReader, _Mapping]] = ..., vape_detector: _Optional[_Union[_graph_models_pb2.VapeDetector, _Mapping]] = ...) -> None: ...

class CamerasInFacility(_message.Message):
    __slots__ = ("levels", "zones", "campuses", "cameras", "badge_readers", "facility_objects")
    LEVELS_FIELD_NUMBER: _ClassVar[int]
    ZONES_FIELD_NUMBER: _ClassVar[int]
    CAMPUSES_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    BADGE_READERS_FIELD_NUMBER: _ClassVar[int]
    FACILITY_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    levels: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Level]
    zones: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Zone]
    campuses: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Campus]
    cameras: _containers.RepeatedCompositeFieldContainer[CameraWithRelationships]
    badge_readers: _containers.RepeatedCompositeFieldContainer[BadgeReaderWithRelationships]
    facility_objects: _containers.RepeatedCompositeFieldContainer[FacilityObjectWithRelationships]
    def __init__(self, levels: _Optional[_Iterable[_Union[_graph_models_pb2.Level, _Mapping]]] = ..., zones: _Optional[_Iterable[_Union[_graph_models_pb2.Zone, _Mapping]]] = ..., campuses: _Optional[_Iterable[_Union[_graph_models_pb2.Campus, _Mapping]]] = ..., cameras: _Optional[_Iterable[_Union[CameraWithRelationships, _Mapping]]] = ..., badge_readers: _Optional[_Iterable[_Union[BadgeReaderWithRelationships, _Mapping]]] = ..., facility_objects: _Optional[_Iterable[_Union[FacilityObjectWithRelationships, _Mapping]]] = ...) -> None: ...

class FFProbRequest(_message.Message):
    __slots__ = ("id", "cameras")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    id: str
    cameras: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Camera]
    def __init__(self, id: _Optional[str] = ..., cameras: _Optional[_Iterable[_Union[_graph_models_pb2.Camera, _Mapping]]] = ...) -> None: ...

class FFProbResponse(_message.Message):
    __slots__ = ("id", "request_id", "camera_id", "output", "error", "online", "timestamp")
    class OutputEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ErrorEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    request_id: str
    camera_id: str
    output: _containers.ScalarMap[str, str]
    error: _containers.ScalarMap[str, str]
    online: bool
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., request_id: _Optional[str] = ..., camera_id: _Optional[str] = ..., output: _Optional[_Mapping[str, str]] = ..., error: _Optional[_Mapping[str, str]] = ..., online: bool = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class VideoIngestFragment(_message.Message):
    __slots__ = ("customer_id", "facility_id", "camera_id", "s3_uri", "duration", "start_ts", "tags")
    class TagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    S3_URI_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    START_TS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    facility_id: str
    camera_id: str
    s3_uri: str
    duration: float
    start_ts: _timestamp_pb2.Timestamp
    tags: _containers.ScalarMap[str, str]
    def __init__(self, customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., camera_id: _Optional[str] = ..., s3_uri: _Optional[str] = ..., duration: _Optional[float] = ..., start_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CustomRuleEvent(_message.Message):
    __slots__ = ("id", "customer_id", "facility_id", "camera_ids", "rule_setting", "timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_IDS_FIELD_NUMBER: _ClassVar[int]
    RULE_SETTING_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    facility_id: str
    camera_ids: _containers.RepeatedScalarFieldContainer[str]
    rule_setting: _graph_models_pb2.RuleSetting
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., camera_ids: _Optional[_Iterable[str]] = ..., rule_setting: _Optional[_Union[_graph_models_pb2.RuleSetting, _Mapping]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
