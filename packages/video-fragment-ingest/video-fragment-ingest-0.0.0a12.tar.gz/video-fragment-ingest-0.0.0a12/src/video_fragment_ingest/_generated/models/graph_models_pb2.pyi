from google.protobuf import timestamp_pb2 as _timestamp_pb2
from models import ai_models_pb2 as _ai_models_pb2
from models import spatial_models_pb2 as _spatial_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Coordinate(_message.Message):
    __slots__ = ("id", "index", "x", "y")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    id: str
    index: int
    x: float
    y: float
    def __init__(self, id: _Optional[str] = ..., index: _Optional[int] = ..., x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class CustomerList(_message.Message):
    __slots__ = ("customers",)
    CUSTOMERS_FIELD_NUMBER: _ClassVar[int]
    customers: _containers.RepeatedCompositeFieldContainer[Customer]
    def __init__(self, customers: _Optional[_Iterable[_Union[Customer, _Mapping]]] = ...) -> None: ...

class Customer(_message.Message):
    __slots__ = ("id", "name", "users", "facilities", "domain", "audios", "campuses", "is_archived", "user_groups", "roles", "escalation_policy", "shifts", "tokens", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    AUDIOS_FIELD_NUMBER: _ClassVar[int]
    CAMPUSES_FIELD_NUMBER: _ClassVar[int]
    IS_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    USER_GROUPS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    ESCALATION_POLICY_FIELD_NUMBER: _ClassVar[int]
    SHIFTS_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    users: _containers.RepeatedCompositeFieldContainer[User]
    facilities: _containers.RepeatedCompositeFieldContainer[Facility]
    domain: str
    audios: _containers.RepeatedCompositeFieldContainer[SpeechAudio]
    campuses: _containers.RepeatedCompositeFieldContainer[Campus]
    is_archived: bool
    user_groups: _containers.RepeatedCompositeFieldContainer[UserGroup]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    escalation_policy: EscalationPolicy
    shifts: _containers.RepeatedCompositeFieldContainer[Shift]
    tokens: _containers.RepeatedCompositeFieldContainer[Token]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., facilities: _Optional[_Iterable[_Union[Facility, _Mapping]]] = ..., domain: _Optional[str] = ..., audios: _Optional[_Iterable[_Union[SpeechAudio, _Mapping]]] = ..., campuses: _Optional[_Iterable[_Union[Campus, _Mapping]]] = ..., is_archived: bool = ..., user_groups: _Optional[_Iterable[_Union[UserGroup, _Mapping]]] = ..., roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ..., escalation_policy: _Optional[_Union[EscalationPolicy, _Mapping]] = ..., shifts: _Optional[_Iterable[_Union[Shift, _Mapping]]] = ..., tokens: _Optional[_Iterable[_Union[Token, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Token(_message.Message):
    __slots__ = ("id", "name", "hashed_token", "masked_token", "hash_algorithm", "created_by_user_id", "permissions", "revoked", "revoked_at", "revoked_by_user_id", "created", "updated", "last_used")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HASHED_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MASKED_TOKEN_FIELD_NUMBER: _ClassVar[int]
    HASH_ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    REVOKED_AT_FIELD_NUMBER: _ClassVar[int]
    REVOKED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    LAST_USED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    hashed_token: str
    masked_token: str
    hash_algorithm: str
    created_by_user_id: str
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    revoked: bool
    revoked_at: _timestamp_pb2.Timestamp
    revoked_by_user_id: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    last_used: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., hashed_token: _Optional[str] = ..., masked_token: _Optional[str] = ..., hash_algorithm: _Optional[str] = ..., created_by_user_id: _Optional[str] = ..., permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ..., revoked: bool = ..., revoked_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., revoked_by_user_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_used: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Campus(_message.Message):
    __slots__ = ("id", "customer_id", "name", "zones", "cameras", "speakers", "facilities", "coordinates", "multi_lens_cameras", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ZONES_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    SPEAKERS_FIELD_NUMBER: _ClassVar[int]
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    MULTI_LENS_CAMERAS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    name: str
    zones: _containers.RepeatedCompositeFieldContainer[Zone]
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    speakers: _containers.RepeatedCompositeFieldContainer[Speaker]
    facilities: _containers.RepeatedCompositeFieldContainer[Facility]
    coordinates: _containers.RepeatedCompositeFieldContainer[Coordinate]
    multi_lens_cameras: _containers.RepeatedCompositeFieldContainer[MultiLensCamera]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., name: _Optional[str] = ..., zones: _Optional[_Iterable[_Union[Zone, _Mapping]]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., speakers: _Optional[_Iterable[_Union[Speaker, _Mapping]]] = ..., facilities: _Optional[_Iterable[_Union[Facility, _Mapping]]] = ..., coordinates: _Optional[_Iterable[_Union[Coordinate, _Mapping]]] = ..., multi_lens_cameras: _Optional[_Iterable[_Union[MultiLensCamera, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Facility(_message.Message):
    __slots__ = ("customer_id", "id", "name", "street", "city", "state", "zipcode", "longitude", "latitude", "contacts", "floor_plan", "devices", "access_key", "secret_key", "img_url", "region", "time_zone", "campus_id", "cameras", "multi_lens_cameras", "show_campus", "rule_settings", "work_hours", "disable_rules", "escalation_policy", "created", "updated")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STREET_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ZIPCODE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    FLOOR_PLAN_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    IMG_URL_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    TIME_ZONE_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    MULTI_LENS_CAMERAS_FIELD_NUMBER: _ClassVar[int]
    SHOW_CAMPUS_FIELD_NUMBER: _ClassVar[int]
    RULE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    WORK_HOURS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_RULES_FIELD_NUMBER: _ClassVar[int]
    ESCALATION_POLICY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    id: str
    name: str
    street: str
    city: str
    state: str
    zipcode: str
    longitude: float
    latitude: float
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    floor_plan: FloorPlan
    devices: _containers.RepeatedCompositeFieldContainer[Device]
    access_key: str
    secret_key: str
    img_url: str
    region: str
    time_zone: str
    campus_id: str
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    multi_lens_cameras: _containers.RepeatedCompositeFieldContainer[MultiLensCamera]
    show_campus: bool
    rule_settings: _containers.RepeatedCompositeFieldContainer[RuleSetting]
    work_hours: _containers.RepeatedCompositeFieldContainer[WorkHours]
    disable_rules: bool
    escalation_policy: EscalationPolicy
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, customer_id: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., street: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., zipcode: _Optional[str] = ..., longitude: _Optional[float] = ..., latitude: _Optional[float] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., floor_plan: _Optional[_Union[FloorPlan, _Mapping]] = ..., devices: _Optional[_Iterable[_Union[Device, _Mapping]]] = ..., access_key: _Optional[str] = ..., secret_key: _Optional[str] = ..., img_url: _Optional[str] = ..., region: _Optional[str] = ..., time_zone: _Optional[str] = ..., campus_id: _Optional[str] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., multi_lens_cameras: _Optional[_Iterable[_Union[MultiLensCamera, _Mapping]]] = ..., show_campus: bool = ..., rule_settings: _Optional[_Iterable[_Union[RuleSetting, _Mapping]]] = ..., work_hours: _Optional[_Iterable[_Union[WorkHours, _Mapping]]] = ..., disable_rules: bool = ..., escalation_policy: _Optional[_Union[EscalationPolicy, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DisableCamerasLog(_message.Message):
    __slots__ = ("id", "cameras", "facility", "user", "duration", "created", "updated", "end")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    id: str
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    facility: Facility
    user: User
    duration: int
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., facility: _Optional[_Union[Facility, _Mapping]] = ..., user: _Optional[_Union[User, _Mapping]] = ..., duration: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeviceCluster(_message.Message):
    __slots__ = ("id", "name", "devices", "customer_id", "facility_id", "position_x", "position_y", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    devices: _containers.RepeatedCompositeFieldContainer[Device]
    customer_id: str
    facility_id: str
    position_x: float
    position_y: float
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., devices: _Optional[_Iterable[_Union[Device, _Mapping]]] = ..., customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Device(_message.Message):
    __slots__ = ("id", "sw_version", "facility_id", "name", "type", "system_uuid", "arn", "status", "cameras", "status_updated", "position_x", "position_y", "customer_id", "cluster_id", "speakers", "subnet_mask", "capacity", "created", "updated")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TYPE: _ClassVar[Device.Type]
        NANO: _ClassVar[Device.Type]
        XAVIER: _ClassVar[Device.Type]
        XAVIER_NX: _ClassVar[Device.Type]
        XAVIER_AGX: _ClassVar[Device.Type]
        X86_A100: _ClassVar[Device.Type]
    UNKNOWN_TYPE: Device.Type
    NANO: Device.Type
    XAVIER: Device.Type
    XAVIER_NX: Device.Type
    XAVIER_AGX: Device.Type
    X86_A100: Device.Type
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Device.Status]
        OFFLINE: _ClassVar[Device.Status]
        ONLINE: _ClassVar[Device.Status]
        UPDATING: _ClassVar[Device.Status]
        PAIRING: _ClassVar[Device.Status]
    UNKNOWN: Device.Status
    OFFLINE: Device.Status
    ONLINE: Device.Status
    UPDATING: Device.Status
    PAIRING: Device.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    SW_VERSION_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_UUID_FIELD_NUMBER: _ClassVar[int]
    ARN_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    STATUS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    SPEAKERS_FIELD_NUMBER: _ClassVar[int]
    SUBNET_MASK_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    sw_version: str
    facility_id: str
    name: str
    type: Device.Type
    system_uuid: str
    arn: str
    status: Device.Status
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    status_updated: _timestamp_pb2.Timestamp
    position_x: float
    position_y: float
    customer_id: str
    cluster_id: str
    speakers: _containers.RepeatedCompositeFieldContainer[Speaker]
    subnet_mask: str
    capacity: int
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., sw_version: _Optional[str] = ..., facility_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[Device.Type, str]] = ..., system_uuid: _Optional[str] = ..., arn: _Optional[str] = ..., status: _Optional[_Union[Device.Status, str]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., status_updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., customer_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., speakers: _Optional[_Iterable[_Union[Speaker, _Mapping]]] = ..., subnet_mask: _Optional[str] = ..., capacity: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CameraManufacturer(_message.Message):
    __slots__ = ("id", "name", "models", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    models: _containers.RepeatedCompositeFieldContainer[CameraModel]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., models: _Optional[_Iterable[_Union[CameraModel, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CameraModel(_message.Message):
    __slots__ = ("id", "name", "lenses", "is_ptz", "has_dynamic_zoom", "rtsp_url_templates", "focal_length_mm", "sensor_width_mm", "sensor_height_mm", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LENSES_FIELD_NUMBER: _ClassVar[int]
    IS_PTZ_FIELD_NUMBER: _ClassVar[int]
    HAS_DYNAMIC_ZOOM_FIELD_NUMBER: _ClassVar[int]
    RTSP_URL_TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    FOCAL_LENGTH_MM_FIELD_NUMBER: _ClassVar[int]
    SENSOR_WIDTH_MM_FIELD_NUMBER: _ClassVar[int]
    SENSOR_HEIGHT_MM_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    lenses: int
    is_ptz: bool
    has_dynamic_zoom: bool
    rtsp_url_templates: str
    focal_length_mm: float
    sensor_width_mm: float
    sensor_height_mm: float
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., lenses: _Optional[int] = ..., is_ptz: bool = ..., has_dynamic_zoom: bool = ..., rtsp_url_templates: _Optional[str] = ..., focal_length_mm: _Optional[float] = ..., sensor_width_mm: _Optional[float] = ..., sensor_height_mm: _Optional[float] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MultiLensCamera(_message.Message):
    __slots__ = ("id", "name", "cameras", "position_x", "position_y", "customer_id", "facility_id", "device_id", "elevation", "yaw", "pitch", "fov", "aspect", "range", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_FIELD_NUMBER: _ClassVar[int]
    YAW_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    FOV_FIELD_NUMBER: _ClassVar[int]
    ASPECT_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    position_x: float
    position_y: float
    customer_id: str
    facility_id: str
    device_id: str
    elevation: float
    yaw: float
    pitch: float
    fov: float
    aspect: float
    range: float
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., device_id: _Optional[str] = ..., elevation: _Optional[float] = ..., yaw: _Optional[float] = ..., pitch: _Optional[float] = ..., fov: _Optional[float] = ..., aspect: _Optional[float] = ..., range: _Optional[float] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Camera(_message.Message):
    __slots__ = ("id", "mac_address", "name", "ip", "port", "username", "password", "model_name", "fps", "resolution_height", "resolution_width", "encoding", "arn", "device_id", "rtsp_url", "status", "status_updated", "magicplan_uid", "position_x", "position_y", "elevation", "yaw", "pitch", "fov", "aspect", "range", "type", "facility_id", "inference_status", "streaming_status", "recording_status", "masks", "latitude", "longitude", "multi_lens_camera_id", "rotation", "kvs_stream_arn", "statistic", "decomposer_regions", "created", "updated", "test_mode", "controller", "subnet_mask", "use_tcp", "focal_length_mm", "sensor_width_mm", "sensor_height_mm", "model", "last_calibrated", "disabled", "spatial_calibration_data", "continuous_video_upload", "customer_id")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNKNOWN: _ClassVar[Camera.Status]
        OFFLINE: _ClassVar[Camera.Status]
        IDLE: _ClassVar[Camera.Status]
        STREAMING: _ClassVar[Camera.Status]
    STATUS_UNKNOWN: Camera.Status
    OFFLINE: Camera.Status
    IDLE: Camera.Status
    STREAMING: Camera.Status
    class CameraType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CAMERA_TYPE_UNKNOWN: _ClassVar[Camera.CameraType]
        WALL: _ClassVar[Camera.CameraType]
        CEILING: _ClassVar[Camera.CameraType]
        MULTI_LENS: _ClassVar[Camera.CameraType]
        FISHEYE: _ClassVar[Camera.CameraType]
    CAMERA_TYPE_UNKNOWN: Camera.CameraType
    WALL: Camera.CameraType
    CEILING: Camera.CameraType
    MULTI_LENS: Camera.CameraType
    FISHEYE: Camera.CameraType
    class Controller(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_SOURCE: _ClassVar[Camera.Controller]
        EDGE: _ClassVar[Camera.Controller]
        CLOUD: _ClassVar[Camera.Controller]
    UNKNOWN_SOURCE: Camera.Controller
    EDGE: Camera.Controller
    CLOUD: Camera.Controller
    class TestMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TEST_CASE: _ClassVar[Camera.TestMode]
        WEAPON: _ClassVar[Camera.TestMode]
        MEDICAL: _ClassVar[Camera.TestMode]
        NONE: _ClassVar[Camera.TestMode]
    UNKNOWN_TEST_CASE: Camera.TestMode
    WEAPON: Camera.TestMode
    MEDICAL: Camera.TestMode
    NONE: Camera.TestMode
    ID_FIELD_NUMBER: _ClassVar[int]
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    FPS_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_WIDTH_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    ARN_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    RTSP_URL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_FIELD_NUMBER: _ClassVar[int]
    YAW_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    FOV_FIELD_NUMBER: _ClassVar[int]
    ASPECT_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    INFERENCE_STATUS_FIELD_NUMBER: _ClassVar[int]
    STREAMING_STATUS_FIELD_NUMBER: _ClassVar[int]
    RECORDING_STATUS_FIELD_NUMBER: _ClassVar[int]
    MASKS_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    MULTI_LENS_CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    KVS_STREAM_ARN_FIELD_NUMBER: _ClassVar[int]
    STATISTIC_FIELD_NUMBER: _ClassVar[int]
    DECOMPOSER_REGIONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    TEST_MODE_FIELD_NUMBER: _ClassVar[int]
    CONTROLLER_FIELD_NUMBER: _ClassVar[int]
    SUBNET_MASK_FIELD_NUMBER: _ClassVar[int]
    USE_TCP_FIELD_NUMBER: _ClassVar[int]
    FOCAL_LENGTH_MM_FIELD_NUMBER: _ClassVar[int]
    SENSOR_WIDTH_MM_FIELD_NUMBER: _ClassVar[int]
    SENSOR_HEIGHT_MM_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    LAST_CALIBRATED_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_CALIBRATION_DATA_FIELD_NUMBER: _ClassVar[int]
    CONTINUOUS_VIDEO_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    mac_address: str
    name: str
    ip: str
    port: str
    username: str
    password: str
    model_name: str
    fps: int
    resolution_height: int
    resolution_width: int
    encoding: str
    arn: str
    device_id: str
    rtsp_url: str
    status: Camera.Status
    status_updated: _timestamp_pb2.Timestamp
    magicplan_uid: str
    position_x: float
    position_y: float
    elevation: float
    yaw: float
    pitch: float
    fov: float
    aspect: float
    range: float
    type: Camera.CameraType
    facility_id: str
    inference_status: Camera.Status
    streaming_status: Camera.Status
    recording_status: Camera.Status
    masks: _containers.RepeatedCompositeFieldContainer[Mask]
    latitude: float
    longitude: float
    multi_lens_camera_id: str
    rotation: int
    kvs_stream_arn: str
    statistic: str
    decomposer_regions: _containers.RepeatedCompositeFieldContainer[DecomposerRegion]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    test_mode: Camera.TestMode
    controller: Camera.Controller
    subnet_mask: str
    use_tcp: bool
    focal_length_mm: float
    sensor_width_mm: float
    sensor_height_mm: float
    model: CameraModel
    last_calibrated: _timestamp_pb2.Timestamp
    disabled: bool
    spatial_calibration_data: _spatial_models_pb2.SpatialCalibrationData
    continuous_video_upload: bool
    customer_id: str
    def __init__(self, id: _Optional[str] = ..., mac_address: _Optional[str] = ..., name: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., model_name: _Optional[str] = ..., fps: _Optional[int] = ..., resolution_height: _Optional[int] = ..., resolution_width: _Optional[int] = ..., encoding: _Optional[str] = ..., arn: _Optional[str] = ..., device_id: _Optional[str] = ..., rtsp_url: _Optional[str] = ..., status: _Optional[_Union[Camera.Status, str]] = ..., status_updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., magicplan_uid: _Optional[str] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., elevation: _Optional[float] = ..., yaw: _Optional[float] = ..., pitch: _Optional[float] = ..., fov: _Optional[float] = ..., aspect: _Optional[float] = ..., range: _Optional[float] = ..., type: _Optional[_Union[Camera.CameraType, str]] = ..., facility_id: _Optional[str] = ..., inference_status: _Optional[_Union[Camera.Status, str]] = ..., streaming_status: _Optional[_Union[Camera.Status, str]] = ..., recording_status: _Optional[_Union[Camera.Status, str]] = ..., masks: _Optional[_Iterable[_Union[Mask, _Mapping]]] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., multi_lens_camera_id: _Optional[str] = ..., rotation: _Optional[int] = ..., kvs_stream_arn: _Optional[str] = ..., statistic: _Optional[str] = ..., decomposer_regions: _Optional[_Iterable[_Union[DecomposerRegion, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., test_mode: _Optional[_Union[Camera.TestMode, str]] = ..., controller: _Optional[_Union[Camera.Controller, str]] = ..., subnet_mask: _Optional[str] = ..., use_tcp: bool = ..., focal_length_mm: _Optional[float] = ..., sensor_width_mm: _Optional[float] = ..., sensor_height_mm: _Optional[float] = ..., model: _Optional[_Union[CameraModel, _Mapping]] = ..., last_calibrated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., disabled: bool = ..., spatial_calibration_data: _Optional[_Union[_spatial_models_pb2.SpatialCalibrationData, _Mapping]] = ..., continuous_video_upload: bool = ..., customer_id: _Optional[str] = ...) -> None: ...

class DecomposerRegion(_message.Message):
    __slots__ = ("id", "x", "y", "w", "h")
    ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    W_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    id: str
    x: float
    y: float
    w: float
    h: float
    def __init__(self, id: _Optional[str] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., w: _Optional[float] = ..., h: _Optional[float] = ...) -> None: ...

class Speaker(_message.Message):
    __slots__ = ("id", "mac_address", "name", "ip", "port", "username", "password", "model_name", "volume_level", "sip_address", "device_id", "magicplan_uid", "position_x", "position_y", "elevation", "yaw", "pitch", "facility_id", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    VOLUME_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SIP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_FIELD_NUMBER: _ClassVar[int]
    YAW_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    mac_address: str
    name: str
    ip: str
    port: str
    username: str
    password: str
    model_name: str
    volume_level: int
    sip_address: str
    device_id: str
    magicplan_uid: str
    position_x: float
    position_y: float
    elevation: float
    yaw: float
    pitch: float
    facility_id: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., mac_address: _Optional[str] = ..., name: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., model_name: _Optional[str] = ..., volume_level: _Optional[int] = ..., sip_address: _Optional[str] = ..., device_id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., elevation: _Optional[float] = ..., yaw: _Optional[float] = ..., pitch: _Optional[float] = ..., facility_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Contact(_message.Message):
    __slots__ = ("id", "first_name", "last_name", "position", "email", "phone", "priority", "img_url", "contact_points", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    IMG_URL_FIELD_NUMBER: _ClassVar[int]
    CONTACT_POINTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    first_name: str
    last_name: str
    position: str
    email: str
    phone: str
    priority: int
    img_url: str
    contact_points: _containers.RepeatedCompositeFieldContainer[ContactPoint]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., position: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., priority: _Optional[int] = ..., img_url: _Optional[str] = ..., contact_points: _Optional[_Iterable[_Union[ContactPoint, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ContactPoint(_message.Message):
    __slots__ = ("id", "email", "phone_number")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    phone_number: str
    def __init__(self, id: _Optional[str] = ..., email: _Optional[str] = ..., phone_number: _Optional[str] = ...) -> None: ...

class Export(_message.Message):
    __slots__ = ("id", "bucket", "key", "url")
    ID_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    bucket: str
    key: str
    url: str
    def __init__(self, id: _Optional[str] = ..., bucket: _Optional[str] = ..., key: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class IncidentList(_message.Message):
    __slots__ = ("incidents",)
    INCIDENTS_FIELD_NUMBER: _ClassVar[int]
    incidents: _containers.RepeatedCompositeFieldContainer[Incident]
    def __init__(self, incidents: _Optional[_Iterable[_Union[Incident, _Mapping]]] = ...) -> None: ...

class ViolationTrigger(_message.Message):
    __slots__ = ("id", "type", "severity", "facility_id", "camera_id", "confidence", "timestamp", "rule_id", "risk_score", "rule", "title", "zone", "triggered_by", "is_manual_trigger", "frames", "object_classes", "objects_of_interest", "system_event_id")
    class TriggeredBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ViolationTrigger.TriggeredBy]
        ZONE_WIDE_RULE: _ClassVar[ViolationTrigger.TriggeredBy]
        FACILITY_WIDE_RULE: _ClassVar[ViolationTrigger.TriggeredBy]
        LEVEL_WIDE_RULE: _ClassVar[ViolationTrigger.TriggeredBy]
        ON_DEMAND: _ClassVar[ViolationTrigger.TriggeredBy]
    UNKNOWN: ViolationTrigger.TriggeredBy
    ZONE_WIDE_RULE: ViolationTrigger.TriggeredBy
    FACILITY_WIDE_RULE: ViolationTrigger.TriggeredBy
    LEVEL_WIDE_RULE: ViolationTrigger.TriggeredBy
    ON_DEMAND: ViolationTrigger.TriggeredBy
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RULE_ID_FIELD_NUMBER: _ClassVar[int]
    RISK_SCORE_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    TRIGGERED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_MANUAL_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASSES_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: Incident.Type
    severity: Incident.Severity
    facility_id: str
    camera_id: str
    confidence: float
    timestamp: _timestamp_pb2.Timestamp
    rule_id: str
    risk_score: float
    rule: RuleSetting
    title: str
    zone: Zone
    triggered_by: ViolationTrigger.TriggeredBy
    is_manual_trigger: bool
    frames: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.InferenceFrame]
    object_classes: _containers.RepeatedScalarFieldContainer[_ai_models_pb2.DetectedObject.ObjectClass]
    objects_of_interest: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.DetectedObject]
    system_event_id: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[Incident.Type, str]] = ..., severity: _Optional[_Union[Incident.Severity, str]] = ..., facility_id: _Optional[str] = ..., camera_id: _Optional[str] = ..., confidence: _Optional[float] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., rule_id: _Optional[str] = ..., risk_score: _Optional[float] = ..., rule: _Optional[_Union[RuleSetting, _Mapping]] = ..., title: _Optional[str] = ..., zone: _Optional[_Union[Zone, _Mapping]] = ..., triggered_by: _Optional[_Union[ViolationTrigger.TriggeredBy, str]] = ..., is_manual_trigger: bool = ..., frames: _Optional[_Iterable[_Union[_ai_models_pb2.InferenceFrame, _Mapping]]] = ..., object_classes: _Optional[_Iterable[_Union[_ai_models_pb2.DetectedObject.ObjectClass, str]]] = ..., objects_of_interest: _Optional[_Iterable[_Union[_ai_models_pb2.DetectedObject, _Mapping]]] = ..., system_event_id: _Optional[str] = ...) -> None: ...

class FacilitySnapshot(_message.Message):
    __slots__ = ("id", "floor_plan", "outdoor", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    FLOOR_PLAN_FIELD_NUMBER: _ClassVar[int]
    OUTDOOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    floor_plan: str
    outdoor: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., floor_plan: _Optional[str] = ..., outdoor: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Incident(_message.Message):
    __slots__ = ("id", "facility_id", "type", "risk_score", "severity", "status", "start_timestamp", "end_timestamp", "events", "activity_logs", "customer_id", "floor_plan", "rule_id", "title", "frames", "zone_type", "room", "customer", "facility", "zone", "trigger_camera_id", "confirmed_by", "escalated", "rule_setting_id", "progress", "cameras", "trigger_rule_id", "export", "snapshot", "auto_911", "emergency_progress", "location_id", "assignees", "trigger_rule", "tracking_job", "incident_status", "created", "updated")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_STATUS: _ClassVar[Incident.Status]
        OPEN: _ClassVar[Incident.Status]
        IN_REVIEW: _ClassVar[Incident.Status]
        FALSE_POSITIVE: _ClassVar[Incident.Status]
        ESCALATION_FAILED: _ClassVar[Incident.Status]
        ACTIVE: _ClassVar[Incident.Status]
        RECEIVED: _ClassVar[Incident.Status]
        CONFIRMED: _ClassVar[Incident.Status]
        POC_IN_REVIEW: _ClassVar[Incident.Status]
        CLOSED: _ClassVar[Incident.Status]
        SEALED: _ClassVar[Incident.Status]
        AI_VALIDATION: _ClassVar[Incident.Status]
        AI_FALSE_POSITIVE: _ClassVar[Incident.Status]
    UNKNOWN_STATUS: Incident.Status
    OPEN: Incident.Status
    IN_REVIEW: Incident.Status
    FALSE_POSITIVE: Incident.Status
    ESCALATION_FAILED: Incident.Status
    ACTIVE: Incident.Status
    RECEIVED: Incident.Status
    CONFIRMED: Incident.Status
    POC_IN_REVIEW: Incident.Status
    CLOSED: Incident.Status
    SEALED: Incident.Status
    AI_VALIDATION: Incident.Status
    AI_FALSE_POSITIVE: Incident.Status
    class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_SEVERITY: _ClassVar[Incident.Severity]
        LEVEL_1: _ClassVar[Incident.Severity]
        LEVEL_2: _ClassVar[Incident.Severity]
        LEVEL_3: _ClassVar[Incident.Severity]
        LEVEL_4: _ClassVar[Incident.Severity]
        LEVEL_5: _ClassVar[Incident.Severity]
    UNKNOWN_SEVERITY: Incident.Severity
    LEVEL_1: Incident.Severity
    LEVEL_2: Incident.Severity
    LEVEL_3: Incident.Severity
    LEVEL_4: Incident.Severity
    LEVEL_5: Incident.Severity
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TYPE: _ClassVar[Incident.Type]
        ROBBERY: _ClassVar[Incident.Type]
        INTRUSION: _ClassVar[Incident.Type]
        ARMED_PERSON: _ClassVar[Incident.Type]
        MEDICAL_EMERGENCY: _ClassVar[Incident.Type]
        OCCUPANCY_LIMIT_REACHED: _ClassVar[Incident.Type]
        VEHICLE_DETECTION: _ClassVar[Incident.Type]
        OBJECT_LEFT_BEHIND: _ClassVar[Incident.Type]
        LOITERING: _ClassVar[Incident.Type]
        FIGHTING: _ClassVar[Incident.Type]
        CAR_LOITERING: _ClassVar[Incident.Type]
        TRACKING: _ClassVar[Incident.Type]
    UNKNOWN_TYPE: Incident.Type
    ROBBERY: Incident.Type
    INTRUSION: Incident.Type
    ARMED_PERSON: Incident.Type
    MEDICAL_EMERGENCY: Incident.Type
    OCCUPANCY_LIMIT_REACHED: Incident.Type
    VEHICLE_DETECTION: Incident.Type
    OBJECT_LEFT_BEHIND: Incident.Type
    LOITERING: Incident.Type
    FIGHTING: Incident.Type
    CAR_LOITERING: Incident.Type
    TRACKING: Incident.Type
    ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RISK_SCORE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_LOGS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FLOOR_PLAN_FIELD_NUMBER: _ClassVar[int]
    RULE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    ZONE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIRMED_BY_FIELD_NUMBER: _ClassVar[int]
    ESCALATED_FIELD_NUMBER: _ClassVar[int]
    RULE_SETTING_ID_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_RULE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPORT_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    AUTO_911_FIELD_NUMBER: _ClassVar[int]
    EMERGENCY_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEES_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_RULE_FIELD_NUMBER: _ClassVar[int]
    TRACKING_JOB_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    facility_id: str
    type: Incident.Type
    risk_score: float
    severity: Incident.Severity
    status: Incident.Status
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    events: _containers.RepeatedCompositeFieldContainer[Event]
    activity_logs: _containers.RepeatedCompositeFieldContainer[ActivityLog]
    customer_id: str
    floor_plan: str
    rule_id: str
    title: str
    frames: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.InferenceFrame]
    zone_type: int
    room: str
    customer: Customer
    facility: Facility
    zone: Zone
    trigger_camera_id: str
    confirmed_by: str
    escalated: _containers.RepeatedCompositeFieldContainer[Contact]
    rule_setting_id: str
    progress: _containers.RepeatedCompositeFieldContainer[IncidentProgress]
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    trigger_rule_id: str
    export: Export
    snapshot: FacilitySnapshot
    auto_911: bool
    emergency_progress: _containers.RepeatedCompositeFieldContainer[EmergencyCallProgress]
    location_id: str
    assignees: _containers.RepeatedCompositeFieldContainer[IncidentAssignment]
    trigger_rule: str
    tracking_job: ObjectOfInterestTrackingJob
    incident_status: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., facility_id: _Optional[str] = ..., type: _Optional[_Union[Incident.Type, str]] = ..., risk_score: _Optional[float] = ..., severity: _Optional[_Union[Incident.Severity, str]] = ..., status: _Optional[_Union[Incident.Status, str]] = ..., start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ..., activity_logs: _Optional[_Iterable[_Union[ActivityLog, _Mapping]]] = ..., customer_id: _Optional[str] = ..., floor_plan: _Optional[str] = ..., rule_id: _Optional[str] = ..., title: _Optional[str] = ..., frames: _Optional[_Iterable[_Union[_ai_models_pb2.InferenceFrame, _Mapping]]] = ..., zone_type: _Optional[int] = ..., room: _Optional[str] = ..., customer: _Optional[_Union[Customer, _Mapping]] = ..., facility: _Optional[_Union[Facility, _Mapping]] = ..., zone: _Optional[_Union[Zone, _Mapping]] = ..., trigger_camera_id: _Optional[str] = ..., confirmed_by: _Optional[str] = ..., escalated: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., rule_setting_id: _Optional[str] = ..., progress: _Optional[_Iterable[_Union[IncidentProgress, _Mapping]]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., trigger_rule_id: _Optional[str] = ..., export: _Optional[_Union[Export, _Mapping]] = ..., snapshot: _Optional[_Union[FacilitySnapshot, _Mapping]] = ..., auto_911: bool = ..., emergency_progress: _Optional[_Iterable[_Union[EmergencyCallProgress, _Mapping]]] = ..., location_id: _Optional[str] = ..., assignees: _Optional[_Iterable[_Union[IncidentAssignment, _Mapping]]] = ..., trigger_rule: _Optional[str] = ..., tracking_job: _Optional[_Union[ObjectOfInterestTrackingJob, _Mapping]] = ..., incident_status: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IncidentAssignment(_message.Message):
    __slots__ = ("id", "assignee", "receipt", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    assignee: User
    receipt: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., assignee: _Optional[_Union[User, _Mapping]] = ..., receipt: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EmergencyCallProgress(_message.Message):
    __slots__ = ("id", "incident_id", "user", "status", "created")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[EmergencyCallProgress.Status]
        CALL_PLACED: _ClassVar[EmergencyCallProgress.Status]
        INITIATE: _ClassVar[EmergencyCallProgress.Status]
        CONFIRM: _ClassVar[EmergencyCallProgress.Status]
        CANCEL: _ClassVar[EmergencyCallProgress.Status]
        COMPLETE: _ClassVar[EmergencyCallProgress.Status]
        RETRY: _ClassVar[EmergencyCallProgress.Status]
        TIMEOUT: _ClassVar[EmergencyCallProgress.Status]
        CALL_END: _ClassVar[EmergencyCallProgress.Status]
    UNKNOWN: EmergencyCallProgress.Status
    CALL_PLACED: EmergencyCallProgress.Status
    INITIATE: EmergencyCallProgress.Status
    CONFIRM: EmergencyCallProgress.Status
    CANCEL: EmergencyCallProgress.Status
    COMPLETE: EmergencyCallProgress.Status
    RETRY: EmergencyCallProgress.Status
    TIMEOUT: EmergencyCallProgress.Status
    CALL_END: EmergencyCallProgress.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    incident_id: str
    user: User
    status: EmergencyCallProgress.Status
    created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., incident_id: _Optional[str] = ..., user: _Optional[_Union[User, _Mapping]] = ..., status: _Optional[_Union[EmergencyCallProgress.Status, str]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IncidentProgress(_message.Message):
    __slots__ = ("status", "created", "id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    status: Incident.Status
    created: _timestamp_pb2.Timestamp
    id: str
    def __init__(self, status: _Optional[_Union[Incident.Status, str]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class IncidentTrigger(_message.Message):
    __slots__ = ("rule", "camera", "timestamp", "id", "frame")
    RULE_FIELD_NUMBER: _ClassVar[int]
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    rule: RuleSetting
    camera: Camera
    timestamp: _timestamp_pb2.Timestamp
    id: str
    frame: _ai_models_pb2.InferenceFrame
    def __init__(self, rule: _Optional[_Union[RuleSetting, _Mapping]] = ..., camera: _Optional[_Union[Camera, _Mapping]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., id: _Optional[str] = ..., frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ...) -> None: ...

class IncidentEventList(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[IncidentEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[IncidentEvent, _Mapping]]] = ...) -> None: ...

class IncidentEvent(_message.Message):
    __slots__ = ("id", "incident_id", "comments", "timestamp", "customer_id", "frame", "log", "media", "tracking_record", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    TRACKING_RECORD_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    incident_id: str
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    timestamp: _timestamp_pb2.Timestamp
    customer_id: str
    frame: _ai_models_pb2.InferenceFrame
    log: ActivityLog
    media: MediaChunk
    tracking_record: ObjectTrackingRecord
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., incident_id: _Optional[str] = ..., comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., customer_id: _Optional[str] = ..., frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ..., log: _Optional[_Union[ActivityLog, _Mapping]] = ..., media: _Optional[_Union[MediaChunk, _Mapping]] = ..., tracking_record: _Optional[_Union[ObjectTrackingRecord, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ObjectTrackingRecord(_message.Message):
    __slots__ = ("id", "frame_id", "frame_url", "description", "object_of_interest")
    ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    id: str
    frame_id: str
    frame_url: str
    description: str
    object_of_interest: _ai_models_pb2.DetectedObject
    def __init__(self, id: _Optional[str] = ..., frame_id: _Optional[str] = ..., frame_url: _Optional[str] = ..., description: _Optional[str] = ..., object_of_interest: _Optional[_Union[_ai_models_pb2.DetectedObject, _Mapping]] = ...) -> None: ...

class IncidentViewerSession(_message.Message):
    __slots__ = ("id", "incident_id", "expiration", "incident", "viewer_identity")
    ID_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_FIELD_NUMBER: _ClassVar[int]
    VIEWER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    incident_id: str
    expiration: _timestamp_pb2.Timestamp
    incident: Incident
    viewer_identity: str
    def __init__(self, id: _Optional[str] = ..., incident_id: _Optional[str] = ..., expiration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., incident: _Optional[_Union[Incident, _Mapping]] = ..., viewer_identity: _Optional[str] = ...) -> None: ...

class Comment(_message.Message):
    __slots__ = ("id", "content", "user_id", "created", "replies", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    REPLIES_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    content: str
    user_id: str
    created: _timestamp_pb2.Timestamp
    replies: _containers.RepeatedCompositeFieldContainer[Comment]
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., content: _Optional[str] = ..., user_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., replies: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Conversation(_message.Message):
    __slots__ = ("id", "incident_id", "conversation_id", "user_id", "contact_id", "phone", "with_participants")
    ID_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTACT_ID_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    WITH_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    incident_id: str
    conversation_id: str
    user_id: str
    contact_id: str
    phone: str
    with_participants: bool
    def __init__(self, id: _Optional[str] = ..., incident_id: _Optional[str] = ..., conversation_id: _Optional[str] = ..., user_id: _Optional[str] = ..., contact_id: _Optional[str] = ..., phone: _Optional[str] = ..., with_participants: bool = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("id", "camera_id", "type", "verification", "confidence", "timestamp", "evidences", "rule", "incident_id", "created", "updated")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TYPE: _ClassVar[Event.Type]
        OBJECT_COUNT: _ClassVar[Event.Type]
        PERSON_DETECTED: _ClassVar[Event.Type]
        ARMED_PERSON_DETECTED: _ClassVar[Event.Type]
    UNKNOWN_TYPE: Event.Type
    OBJECT_COUNT: Event.Type
    PERSON_DETECTED: Event.Type
    ARMED_PERSON_DETECTED: Event.Type
    class Verification(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_VERIFICATION: _ClassVar[Event.Verification]
        POSITIVE: _ClassVar[Event.Verification]
        FALSE_POSITIVE: _ClassVar[Event.Verification]
    UNKNOWN_VERIFICATION: Event.Verification
    POSITIVE: Event.Verification
    FALSE_POSITIVE: Event.Verification
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERIFICATION_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EVIDENCES_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    type: Event.Type
    verification: Event.Verification
    confidence: float
    timestamp: _timestamp_pb2.Timestamp
    evidences: _containers.RepeatedCompositeFieldContainer[MediaChunk]
    rule: RuleSetting
    incident_id: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., type: _Optional[_Union[Event.Type, str]] = ..., verification: _Optional[_Union[Event.Verification, str]] = ..., confidence: _Optional[float] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., evidences: _Optional[_Iterable[_Union[MediaChunk, _Mapping]]] = ..., rule: _Optional[_Union[RuleSetting, _Mapping]] = ..., incident_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MediaChunk(_message.Message):
    __slots__ = ("id", "camera_id", "type", "bucket", "key", "url", "frame_id", "start_timestamp", "end_timestamp", "created", "updated")
    class MediaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[MediaChunk.MediaType]
        VIDEO: _ClassVar[MediaChunk.MediaType]
        IMAGE: _ClassVar[MediaChunk.MediaType]
        FILE: _ClassVar[MediaChunk.MediaType]
    UNKNOWN: MediaChunk.MediaType
    VIDEO: MediaChunk.MediaType
    IMAGE: MediaChunk.MediaType
    FILE: MediaChunk.MediaType
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    type: MediaChunk.MediaType
    bucket: str
    key: str
    url: str
    frame_id: str
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., type: _Optional[_Union[MediaChunk.MediaType, str]] = ..., bucket: _Optional[str] = ..., key: _Optional[str] = ..., url: _Optional[str] = ..., frame_id: _Optional[str] = ..., start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ActivityLog(_message.Message):
    __slots__ = ("id", "description", "type", "event_id", "message", "comments", "incident_id", "media", "user", "created", "updated")
    class ActivityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ActivityLog.ActivityType]
        ACTION: _ClassVar[ActivityLog.ActivityType]
        EVENT: _ClassVar[ActivityLog.ActivityType]
        USER_SESSION: _ClassVar[ActivityLog.ActivityType]
        MESSAGE_SENT: _ClassVar[ActivityLog.ActivityType]
        MESSAGE_RECEIVED: _ClassVar[ActivityLog.ActivityType]
        SYSTEM_MESSAGE: _ClassVar[ActivityLog.ActivityType]
    UNKNOWN: ActivityLog.ActivityType
    ACTION: ActivityLog.ActivityType
    EVENT: ActivityLog.ActivityType
    USER_SESSION: ActivityLog.ActivityType
    MESSAGE_SENT: ActivityLog.ActivityType
    MESSAGE_RECEIVED: ActivityLog.ActivityType
    SYSTEM_MESSAGE: ActivityLog.ActivityType
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    description: str
    type: ActivityLog.ActivityType
    event_id: str
    message: str
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    incident_id: str
    media: _containers.RepeatedCompositeFieldContainer[MediaChunk]
    user: User
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[ActivityLog.ActivityType, str]] = ..., event_id: _Optional[str] = ..., message: _Optional[str] = ..., comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ..., incident_id: _Optional[str] = ..., media: _Optional[_Iterable[_Union[MediaChunk, _Mapping]]] = ..., user: _Optional[_Union[User, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "auth", "first_name", "last_name", "email", "phone", "birthdate", "role", "profile_url", "access_level", "sessions", "customer", "priority", "verified", "profile", "availability", "status", "provider_type", "work_hours", "preferences", "created", "updated")
    class ProviderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_PROVIDER_TYPE: _ClassVar[User.ProviderType]
        EMAIL: _ClassVar[User.ProviderType]
        GOOGLE: _ClassVar[User.ProviderType]
        SAML: _ClassVar[User.ProviderType]
    UNKNOWN_PROVIDER_TYPE: User.ProviderType
    EMAIL: User.ProviderType
    GOOGLE: User.ProviderType
    SAML: User.ProviderType
    class Availability(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_AVAILABILITY: _ClassVar[User.Availability]
        ONLINE: _ClassVar[User.Availability]
        IDLE: _ClassVar[User.Availability]
        OFFLINE: _ClassVar[User.Availability]
    UNKNOWN_AVAILABILITY: User.Availability
    ONLINE: User.Availability
    IDLE: User.Availability
    OFFLINE: User.Availability
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_STATUS: _ClassVar[User.Status]
        ON_DUTY: _ClassVar[User.Status]
        OFF_DUTY: _ClassVar[User.Status]
        AWAY: _ClassVar[User.Status]
    UNKNOWN_STATUS: User.Status
    ON_DUTY: User.Status
    OFF_DUTY: User.Status
    AWAY: User.Status
    class AccessLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[User.AccessLevel]
        MEMBER: _ClassVar[User.AccessLevel]
        ADMIN: _ClassVar[User.AccessLevel]
        VOLT_OPERATOR: _ClassVar[User.AccessLevel]
    UNKNOWN: User.AccessLevel
    MEMBER: User.AccessLevel
    ADMIN: User.AccessLevel
    VOLT_OPERATOR: User.AccessLevel
    class PreferencesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    AUTH_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    BIRTHDATE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_URL_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    WORK_HOURS_FIELD_NUMBER: _ClassVar[int]
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    auth: str
    first_name: str
    last_name: str
    email: str
    phone: str
    birthdate: str
    role: str
    profile_url: str
    access_level: User.AccessLevel
    sessions: _containers.RepeatedCompositeFieldContainer[UserSession]
    customer: Customer
    priority: int
    verified: bool
    profile: UserProfile
    availability: User.Availability
    status: User.Status
    provider_type: User.ProviderType
    work_hours: _containers.RepeatedCompositeFieldContainer[WorkHours]
    preferences: _containers.ScalarMap[str, str]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., auth: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., birthdate: _Optional[str] = ..., role: _Optional[str] = ..., profile_url: _Optional[str] = ..., access_level: _Optional[_Union[User.AccessLevel, str]] = ..., sessions: _Optional[_Iterable[_Union[UserSession, _Mapping]]] = ..., customer: _Optional[_Union[Customer, _Mapping]] = ..., priority: _Optional[int] = ..., verified: bool = ..., profile: _Optional[_Union[UserProfile, _Mapping]] = ..., availability: _Optional[_Union[User.Availability, str]] = ..., status: _Optional[_Union[User.Status, str]] = ..., provider_type: _Optional[_Union[User.ProviderType, str]] = ..., work_hours: _Optional[_Iterable[_Union[WorkHours, _Mapping]]] = ..., preferences: _Optional[_Mapping[str, str]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserProfile(_message.Message):
    __slots__ = ("id", "selected_customer_id", "selected_facility_id", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    SELECTED_CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTED_FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    selected_customer_id: str
    selected_facility_id: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., selected_customer_id: _Optional[str] = ..., selected_facility_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserSession(_message.Message):
    __slots__ = ("id", "user_id", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class APIKey(_message.Message):
    __slots__ = ("id", "name", "key", "secret", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    key: str
    secret: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., key: _Optional[str] = ..., secret: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UserGroup(_message.Message):
    __slots__ = ("id", "name", "users", "facilities", "role", "customer_id", "protected", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PROTECTED_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    users: _containers.RepeatedCompositeFieldContainer[User]
    facilities: _containers.RepeatedCompositeFieldContainer[Facility]
    role: Role
    customer_id: str
    protected: bool
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., facilities: _Optional[_Iterable[_Union[Facility, _Mapping]]] = ..., role: _Optional[_Union[Role, _Mapping]] = ..., customer_id: _Optional[str] = ..., protected: bool = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("id", "name", "description", "permissions", "customer_id", "protected", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PROTECTED_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    customer_id: str
    protected: bool
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ..., customer_id: _Optional[str] = ..., protected: bool = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("id", "name", "category", "description", "created", "updated")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Permission.Category]
        INCIDENT_MANAGEMENT: _ClassVar[Permission.Category]
        FACILITY_MANAGEMENT: _ClassVar[Permission.Category]
        USER_MANAGEMENT: _ClassVar[Permission.Category]
    UNKNOWN: Permission.Category
    INCIDENT_MANAGEMENT: Permission.Category
    FACILITY_MANAGEMENT: Permission.Category
    USER_MANAGEMENT: Permission.Category
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    category: Permission.Category
    description: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., category: _Optional[_Union[Permission.Category, str]] = ..., description: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Daily(_message.Message):
    __slots__ = ("id", "frequency")
    ID_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    id: str
    frequency: int
    def __init__(self, id: _Optional[str] = ..., frequency: _Optional[int] = ...) -> None: ...

class Weekly(_message.Message):
    __slots__ = ("id", "frequency", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    ID_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MONDAY_FIELD_NUMBER: _ClassVar[int]
    TUESDAY_FIELD_NUMBER: _ClassVar[int]
    WEDNESDAY_FIELD_NUMBER: _ClassVar[int]
    THURSDAY_FIELD_NUMBER: _ClassVar[int]
    FRIDAY_FIELD_NUMBER: _ClassVar[int]
    SATURDAY_FIELD_NUMBER: _ClassVar[int]
    SUNDAY_FIELD_NUMBER: _ClassVar[int]
    id: str
    frequency: int
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool
    def __init__(self, id: _Optional[str] = ..., frequency: _Optional[int] = ..., monday: bool = ..., tuesday: bool = ..., wednesday: bool = ..., thursday: bool = ..., friday: bool = ..., saturday: bool = ..., sunday: bool = ...) -> None: ...

class Monthly(_message.Message):
    __slots__ = ("id", "frequency", "day")
    ID_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    DAY_FIELD_NUMBER: _ClassVar[int]
    id: str
    frequency: int
    day: int
    def __init__(self, id: _Optional[str] = ..., frequency: _Optional[int] = ..., day: _Optional[int] = ...) -> None: ...

class WorkHours(_message.Message):
    __slots__ = ("id", "start_time", "end_time", "start_date", "end_date", "daily", "weekly", "monthly", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    DAILY_FIELD_NUMBER: _ClassVar[int]
    WEEKLY_FIELD_NUMBER: _ClassVar[int]
    MONTHLY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    start_time: int
    end_time: int
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    daily: Daily
    weekly: Weekly
    monthly: Monthly
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., start_time: _Optional[int] = ..., end_time: _Optional[int] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., daily: _Optional[_Union[Daily, _Mapping]] = ..., weekly: _Optional[_Union[Weekly, _Mapping]] = ..., monthly: _Optional[_Union[Monthly, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Shift(_message.Message):
    __slots__ = ("id", "work_hours", "name", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    WORK_HOURS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    work_hours: _containers.RepeatedCompositeFieldContainer[WorkHours]
    name: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., work_hours: _Optional[_Iterable[_Union[WorkHours, _Mapping]]] = ..., name: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("id", "magicplan_uid", "index", "x", "y", "z")
    ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    id: str
    magicplan_uid: str
    index: int
    x: float
    y: float
    z: float
    def __init__(self, id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., index: _Optional[int] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class FloorPlan(_message.Message):
    __slots__ = ("id", "facility_id", "plan_id", "magicplan_uid", "label", "levels", "projects", "is_editing", "use_export")
    ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    LEVELS_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    IS_EDITING_FIELD_NUMBER: _ClassVar[int]
    USE_EXPORT_FIELD_NUMBER: _ClassVar[int]
    id: str
    facility_id: str
    plan_id: str
    magicplan_uid: str
    label: str
    levels: _containers.RepeatedCompositeFieldContainer[Level]
    projects: _containers.RepeatedCompositeFieldContainer[MagicPlanProject]
    is_editing: bool
    use_export: bool
    def __init__(self, id: _Optional[str] = ..., facility_id: _Optional[str] = ..., plan_id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., label: _Optional[str] = ..., levels: _Optional[_Iterable[_Union[Level, _Mapping]]] = ..., projects: _Optional[_Iterable[_Union[MagicPlanProject, _Mapping]]] = ..., is_editing: bool = ..., use_export: bool = ...) -> None: ...

class MagicPlanProject(_message.Message):
    __slots__ = ("id", "plan_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    plan_id: str
    def __init__(self, id: _Optional[str] = ..., plan_id: _Optional[str] = ...) -> None: ...

class MagicFloorPlan(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class MagicFloorPlans(_message.Message):
    __slots__ = ("magic_plans",)
    MAGIC_PLANS_FIELD_NUMBER: _ClassVar[int]
    magic_plans: _containers.RepeatedCompositeFieldContainer[MagicFloorPlan]
    def __init__(self, magic_plans: _Optional[_Iterable[_Union[MagicFloorPlan, _Mapping]]] = ...) -> None: ...

class Level(_message.Message):
    __slots__ = ("id", "magicplan_uid", "label", "floor_level", "locations", "walls", "zones", "relative_x", "relative_y", "rotation")
    ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    FLOOR_LEVEL_FIELD_NUMBER: _ClassVar[int]
    LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    WALLS_FIELD_NUMBER: _ClassVar[int]
    ZONES_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_X_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    magicplan_uid: str
    label: str
    floor_level: int
    locations: _containers.RepeatedCompositeFieldContainer[Location]
    walls: _containers.RepeatedCompositeFieldContainer[Wall]
    zones: _containers.RepeatedCompositeFieldContainer[Zone]
    relative_x: float
    relative_y: float
    rotation: float
    def __init__(self, id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., label: _Optional[str] = ..., floor_level: _Optional[int] = ..., locations: _Optional[_Iterable[_Union[Location, _Mapping]]] = ..., walls: _Optional[_Iterable[_Union[Wall, _Mapping]]] = ..., zones: _Optional[_Iterable[_Union[Zone, _Mapping]]] = ..., relative_x: _Optional[float] = ..., relative_y: _Optional[float] = ..., rotation: _Optional[float] = ...) -> None: ...

class Wall(_message.Message):
    __slots__ = ("id", "x1", "x2", "y1", "y2", "height", "thickness", "type")
    class WallType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Wall.WallType]
        INTERIOR: _ClassVar[Wall.WallType]
        EXTERIOR: _ClassVar[Wall.WallType]
    UNKNOWN: Wall.WallType
    INTERIOR: Wall.WallType
    EXTERIOR: Wall.WallType
    ID_FIELD_NUMBER: _ClassVar[int]
    X1_FIELD_NUMBER: _ClassVar[int]
    X2_FIELD_NUMBER: _ClassVar[int]
    Y1_FIELD_NUMBER: _ClassVar[int]
    Y2_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    x1: float
    x2: float
    y1: float
    y2: float
    height: float
    thickness: float
    type: Wall.WallType
    def __init__(self, id: _Optional[str] = ..., x1: _Optional[float] = ..., x2: _Optional[float] = ..., y1: _Optional[float] = ..., y2: _Optional[float] = ..., height: _Optional[float] = ..., thickness: _Optional[float] = ..., type: _Optional[_Union[Wall.WallType, str]] = ...) -> None: ...

class CustomRule(_message.Message):
    __slots__ = ("id", "name", "prompt", "periodicity", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    PERIODICITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    prompt: str
    periodicity: int
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., prompt: _Optional[str] = ..., periodicity: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RuleSetting(_message.Message):
    __slots__ = ("id", "rule_id", "enable", "start_time", "end_time", "min_count", "max_count", "description", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "audio", "rapid_sos", "min_duration", "escalation_policy", "custom_rule")
    ID_FIELD_NUMBER: _ClassVar[int]
    RULE_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    MIN_COUNT_FIELD_NUMBER: _ClassVar[int]
    MAX_COUNT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MONDAY_FIELD_NUMBER: _ClassVar[int]
    TUESDAY_FIELD_NUMBER: _ClassVar[int]
    WEDNESDAY_FIELD_NUMBER: _ClassVar[int]
    THURSDAY_FIELD_NUMBER: _ClassVar[int]
    FRIDAY_FIELD_NUMBER: _ClassVar[int]
    SATURDAY_FIELD_NUMBER: _ClassVar[int]
    SUNDAY_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    RAPID_SOS_FIELD_NUMBER: _ClassVar[int]
    MIN_DURATION_FIELD_NUMBER: _ClassVar[int]
    ESCALATION_POLICY_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_RULE_FIELD_NUMBER: _ClassVar[int]
    id: str
    rule_id: str
    enable: bool
    start_time: int
    end_time: int
    min_count: int
    max_count: int
    description: str
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool
    audio: SpeechAudio
    rapid_sos: bool
    min_duration: int
    escalation_policy: EscalationPolicy
    custom_rule: CustomRule
    def __init__(self, id: _Optional[str] = ..., rule_id: _Optional[str] = ..., enable: bool = ..., start_time: _Optional[int] = ..., end_time: _Optional[int] = ..., min_count: _Optional[int] = ..., max_count: _Optional[int] = ..., description: _Optional[str] = ..., monday: bool = ..., tuesday: bool = ..., wednesday: bool = ..., thursday: bool = ..., friday: bool = ..., saturday: bool = ..., sunday: bool = ..., audio: _Optional[_Union[SpeechAudio, _Mapping]] = ..., rapid_sos: bool = ..., min_duration: _Optional[int] = ..., escalation_policy: _Optional[_Union[EscalationPolicy, _Mapping]] = ..., custom_rule: _Optional[_Union[CustomRule, _Mapping]] = ...) -> None: ...

class Zone(_message.Message):
    __slots__ = ("id", "name", "coordinates", "type", "rule_settings", "cameras", "speakers", "escalation_policy", "badge_readers", "vape_detectors")
    class ZoneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Zone.ZoneType]
        PUBLIC: _ClassVar[Zone.ZoneType]
        SEMI_PUBLIC: _ClassVar[Zone.ZoneType]
        RESTRICTED: _ClassVar[Zone.ZoneType]
        HIGHLY_RESTRICTED: _ClassVar[Zone.ZoneType]
    UNKNOWN: Zone.ZoneType
    PUBLIC: Zone.ZoneType
    SEMI_PUBLIC: Zone.ZoneType
    RESTRICTED: Zone.ZoneType
    HIGHLY_RESTRICTED: Zone.ZoneType
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RULE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    SPEAKERS_FIELD_NUMBER: _ClassVar[int]
    ESCALATION_POLICY_FIELD_NUMBER: _ClassVar[int]
    BADGE_READERS_FIELD_NUMBER: _ClassVar[int]
    VAPE_DETECTORS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    coordinates: _containers.RepeatedCompositeFieldContainer[Coordinate]
    type: Zone.ZoneType
    rule_settings: _containers.RepeatedCompositeFieldContainer[RuleSetting]
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    speakers: _containers.RepeatedCompositeFieldContainer[Speaker]
    escalation_policy: EscalationPolicy
    badge_readers: _containers.RepeatedCompositeFieldContainer[BadgeReader]
    vape_detectors: _containers.RepeatedCompositeFieldContainer[VapeDetector]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., coordinates: _Optional[_Iterable[_Union[Coordinate, _Mapping]]] = ..., type: _Optional[_Union[Zone.ZoneType, str]] = ..., rule_settings: _Optional[_Iterable[_Union[RuleSetting, _Mapping]]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., speakers: _Optional[_Iterable[_Union[Speaker, _Mapping]]] = ..., escalation_policy: _Optional[_Union[EscalationPolicy, _Mapping]] = ..., badge_readers: _Optional[_Iterable[_Union[BadgeReader, _Mapping]]] = ..., vape_detectors: _Optional[_Iterable[_Union[VapeDetector, _Mapping]]] = ...) -> None: ...

class Location(_message.Message):
    __slots__ = ("id", "facility_id", "magicplan_uid", "label", "boundary", "windows", "doors", "furniture", "stairs", "cameras", "devices", "device_clusters", "type", "speakers", "multi_lens_cameras", "badge_readers", "vape_detectors")
    class LocationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Location.LocationType]
        LANDSCAPE: _ClassVar[Location.LocationType]
    UNKNOWN: Location.LocationType
    LANDSCAPE: Location.LocationType
    ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_FIELD_NUMBER: _ClassVar[int]
    WINDOWS_FIELD_NUMBER: _ClassVar[int]
    DOORS_FIELD_NUMBER: _ClassVar[int]
    FURNITURE_FIELD_NUMBER: _ClassVar[int]
    STAIRS_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    DEVICE_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SPEAKERS_FIELD_NUMBER: _ClassVar[int]
    MULTI_LENS_CAMERAS_FIELD_NUMBER: _ClassVar[int]
    BADGE_READERS_FIELD_NUMBER: _ClassVar[int]
    VAPE_DETECTORS_FIELD_NUMBER: _ClassVar[int]
    id: str
    facility_id: str
    magicplan_uid: str
    label: str
    boundary: Boundary
    windows: _containers.RepeatedCompositeFieldContainer[Window]
    doors: _containers.RepeatedCompositeFieldContainer[Door]
    furniture: _containers.RepeatedCompositeFieldContainer[Furniture]
    stairs: _containers.RepeatedCompositeFieldContainer[Stair]
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    devices: _containers.RepeatedCompositeFieldContainer[Device]
    device_clusters: _containers.RepeatedCompositeFieldContainer[DeviceCluster]
    type: Location.LocationType
    speakers: _containers.RepeatedCompositeFieldContainer[Speaker]
    multi_lens_cameras: _containers.RepeatedCompositeFieldContainer[MultiLensCamera]
    badge_readers: _containers.RepeatedCompositeFieldContainer[BadgeReader]
    vape_detectors: _containers.RepeatedCompositeFieldContainer[VapeDetector]
    def __init__(self, id: _Optional[str] = ..., facility_id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., label: _Optional[str] = ..., boundary: _Optional[_Union[Boundary, _Mapping]] = ..., windows: _Optional[_Iterable[_Union[Window, _Mapping]]] = ..., doors: _Optional[_Iterable[_Union[Door, _Mapping]]] = ..., furniture: _Optional[_Iterable[_Union[Furniture, _Mapping]]] = ..., stairs: _Optional[_Iterable[_Union[Stair, _Mapping]]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., devices: _Optional[_Iterable[_Union[Device, _Mapping]]] = ..., device_clusters: _Optional[_Iterable[_Union[DeviceCluster, _Mapping]]] = ..., type: _Optional[_Union[Location.LocationType, str]] = ..., speakers: _Optional[_Iterable[_Union[Speaker, _Mapping]]] = ..., multi_lens_cameras: _Optional[_Iterable[_Union[MultiLensCamera, _Mapping]]] = ..., badge_readers: _Optional[_Iterable[_Union[BadgeReader, _Mapping]]] = ..., vape_detectors: _Optional[_Iterable[_Union[VapeDetector, _Mapping]]] = ...) -> None: ...

class Boundary(_message.Message):
    __slots__ = ("id", "points", "height")
    ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    id: str
    points: _containers.RepeatedCompositeFieldContainer[Point]
    height: float
    def __init__(self, id: _Optional[str] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ..., height: _Optional[float] = ...) -> None: ...

class Window(_message.Message):
    __slots__ = ("id", "magicplan_uid", "label", "left_position_x", "left_position_y", "right_position_x", "right_position_y", "width", "height", "depth", "distance_from_floor", "type", "facility_id")
    class WindowType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Window.WindowType]
        SLIDING: _ClassVar[Window.WindowType]
        HUNG: _ClassVar[Window.WindowType]
        AWNING: _ClassVar[Window.WindowType]
    UNKNOWN: Window.WindowType
    SLIDING: Window.WindowType
    HUNG: Window.WindowType
    AWNING: Window.WindowType
    ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    LEFT_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    LEFT_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    RIGHT_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    RIGHT_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FROM_FLOOR_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    magicplan_uid: str
    label: str
    left_position_x: float
    left_position_y: float
    right_position_x: float
    right_position_y: float
    width: float
    height: float
    depth: float
    distance_from_floor: float
    type: Window.WindowType
    facility_id: str
    def __init__(self, id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., label: _Optional[str] = ..., left_position_x: _Optional[float] = ..., left_position_y: _Optional[float] = ..., right_position_x: _Optional[float] = ..., right_position_y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., depth: _Optional[float] = ..., distance_from_floor: _Optional[float] = ..., type: _Optional[_Union[Window.WindowType, str]] = ..., facility_id: _Optional[str] = ...) -> None: ...

class Door(_message.Message):
    __slots__ = ("id", "magicplan_uid", "twin_magicplan_uid", "leads_to", "label", "hinge_position_x", "hinge_position_y", "latch_position_x", "latch_position_y", "width", "height", "depth", "direction", "type", "facility_id", "closed")
    class DoorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Door.DoorType]
        HINGED_DOOR: _ClassVar[Door.DoorType]
        HINGED_DOUBLE_DOOR: _ClassVar[Door.DoorType]
        GARAGE: _ClassVar[Door.DoorType]
        OPENING: _ClassVar[Door.DoorType]
    UNKNOWN: Door.DoorType
    HINGED_DOOR: Door.DoorType
    HINGED_DOUBLE_DOOR: Door.DoorType
    GARAGE: Door.DoorType
    OPENING: Door.DoorType
    ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    TWIN_MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LEADS_TO_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    HINGE_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    HINGE_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    LATCH_POSITION_X_FIELD_NUMBER: _ClassVar[int]
    LATCH_POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    id: str
    magicplan_uid: str
    twin_magicplan_uid: str
    leads_to: _containers.RepeatedCompositeFieldContainer[Location]
    label: str
    hinge_position_x: float
    hinge_position_y: float
    latch_position_x: float
    latch_position_y: float
    width: float
    height: float
    depth: float
    direction: int
    type: Door.DoorType
    facility_id: str
    closed: bool
    def __init__(self, id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., twin_magicplan_uid: _Optional[str] = ..., leads_to: _Optional[_Iterable[_Union[Location, _Mapping]]] = ..., label: _Optional[str] = ..., hinge_position_x: _Optional[float] = ..., hinge_position_y: _Optional[float] = ..., latch_position_x: _Optional[float] = ..., latch_position_y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., depth: _Optional[float] = ..., direction: _Optional[int] = ..., type: _Optional[_Union[Door.DoorType, str]] = ..., facility_id: _Optional[str] = ..., closed: bool = ...) -> None: ...

class Furniture(_message.Message):
    __slots__ = ("id", "magicplan_uid", "label", "width", "height", "depth", "orientation", "position_x", "position_y", "type", "rotation")
    class FurnitureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Furniture.FurnitureType]
        EXTINGUISHER: _ClassVar[Furniture.FurnitureType]
        EXIT: _ClassVar[Furniture.FurnitureType]
        AED: _ClassVar[Furniture.FurnitureType]
        BADGE_READER: _ClassVar[Furniture.FurnitureType]
        FIRE_PULL: _ClassVar[Furniture.FurnitureType]
        PARTITION_WALL: _ClassVar[Furniture.FurnitureType]
        TABLE: _ClassVar[Furniture.FurnitureType]
        SOFA: _ClassVar[Furniture.FurnitureType]
        BED: _ClassVar[Furniture.FurnitureType]
    UNKNOWN: Furniture.FurnitureType
    EXTINGUISHER: Furniture.FurnitureType
    EXIT: Furniture.FurnitureType
    AED: Furniture.FurnitureType
    BADGE_READER: Furniture.FurnitureType
    FIRE_PULL: Furniture.FurnitureType
    PARTITION_WALL: Furniture.FurnitureType
    TABLE: Furniture.FurnitureType
    SOFA: Furniture.FurnitureType
    BED: Furniture.FurnitureType
    ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    magicplan_uid: str
    label: str
    width: float
    height: float
    depth: float
    orientation: int
    position_x: float
    position_y: float
    type: Furniture.FurnitureType
    rotation: float
    def __init__(self, id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., label: _Optional[str] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., depth: _Optional[float] = ..., orientation: _Optional[int] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., type: _Optional[_Union[Furniture.FurnitureType, str]] = ..., rotation: _Optional[float] = ...) -> None: ...

class BadgeReader(_message.Message):
    __slots__ = ("id", "name", "vendor_id", "vendor_name", "position_x", "position_y", "rotation", "door", "cameras", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    DOOR_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    vendor_id: str
    vendor_name: str
    position_x: float
    position_y: float
    rotation: float
    door: Door
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., vendor_id: _Optional[str] = ..., vendor_name: _Optional[str] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., rotation: _Optional[float] = ..., door: _Optional[_Union[Door, _Mapping]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class VapeDetector(_message.Message):
    __slots__ = ("id", "name", "vendor_id", "vendor_name", "position_x", "position_y", "rotation", "cameras", "manufacturer", "created", "updated")
    class Manufacturer(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[VapeDetector.Manufacturer]
        HALO: _ClassVar[VapeDetector.Manufacturer]
    UNKNOWN: VapeDetector.Manufacturer
    HALO: VapeDetector.Manufacturer
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    vendor_id: str
    vendor_name: str
    position_x: float
    position_y: float
    rotation: float
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    manufacturer: VapeDetector.Manufacturer
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., vendor_id: _Optional[str] = ..., vendor_name: _Optional[str] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., rotation: _Optional[float] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., manufacturer: _Optional[_Union[VapeDetector.Manufacturer, str]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Stair(_message.Message):
    __slots__ = ("id", "magicplan_uid", "label", "steps", "top", "bottom", "position_x", "position_y", "width", "height", "depth", "type")
    class StairType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Stair.StairType]
        STAIRCASE: _ClassVar[Stair.StairType]
        CORNER_LANDING: _ClassVar[Stair.StairType]
        ROUND_U_SHAPED: _ClassVar[Stair.StairType]
        U_SHAPED: _ClassVar[Stair.StairType]
        L_SHAPED_RIGHT: _ClassVar[Stair.StairType]
        L_SHAPED_LEFT: _ClassVar[Stair.StairType]
    UNKNOWN: Stair.StairType
    STAIRCASE: Stair.StairType
    CORNER_LANDING: Stair.StairType
    ROUND_U_SHAPED: Stair.StairType
    U_SHAPED: Stair.StairType
    L_SHAPED_RIGHT: Stair.StairType
    L_SHAPED_LEFT: Stair.StairType
    ID_FIELD_NUMBER: _ClassVar[int]
    MAGICPLAN_UID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    TOP_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    magicplan_uid: str
    label: str
    steps: int
    top: float
    bottom: float
    position_x: float
    position_y: float
    width: float
    height: float
    depth: float
    type: Stair.StairType
    def __init__(self, id: _Optional[str] = ..., magicplan_uid: _Optional[str] = ..., label: _Optional[str] = ..., steps: _Optional[int] = ..., top: _Optional[float] = ..., bottom: _Optional[float] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., depth: _Optional[float] = ..., type: _Optional[_Union[Stair.StairType, str]] = ...) -> None: ...

class Mask(_message.Message):
    __slots__ = ("id", "points", "type", "rules_by_mask")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TYPE: _ClassVar[Mask.Type]
        EXCLUSION: _ClassVar[Mask.Type]
        INCLUSION: _ClassVar[Mask.Type]
    UNKNOWN_TYPE: Mask.Type
    EXCLUSION: Mask.Type
    INCLUSION: Mask.Type
    ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RULES_BY_MASK_FIELD_NUMBER: _ClassVar[int]
    id: str
    points: _containers.RepeatedCompositeFieldContainer[NormalizedPoint]
    type: Mask.Type
    rules_by_mask: _containers.RepeatedCompositeFieldContainer[RuleSetting]
    def __init__(self, id: _Optional[str] = ..., points: _Optional[_Iterable[_Union[NormalizedPoint, _Mapping]]] = ..., type: _Optional[_Union[Mask.Type, str]] = ..., rules_by_mask: _Optional[_Iterable[_Union[RuleSetting, _Mapping]]] = ...) -> None: ...

class NormalizedPoint(_message.Message):
    __slots__ = ("id", "x", "y", "index")
    ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    id: str
    x: float
    y: float
    index: int
    def __init__(self, id: _Optional[str] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., index: _Optional[int] = ...) -> None: ...

class SpeechAudio(_message.Message):
    __slots__ = ("id", "customer_id", "message", "key", "bucket", "url", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    message: str
    key: str
    bucket: str
    url: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., message: _Optional[str] = ..., key: _Optional[str] = ..., bucket: _Optional[str] = ..., url: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class VideoFrame(_message.Message):
    __slots__ = ("id", "camera_id", "bucket", "key", "timestamp", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    bucket: str
    key: str
    timestamp: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., bucket: _Optional[str] = ..., key: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EscalationStep(_message.Message):
    __slots__ = ("id", "index", "shifts", "users", "delay", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SHIFTS_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    DELAY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    index: int
    shifts: _containers.RepeatedCompositeFieldContainer[Shift]
    users: _containers.RepeatedCompositeFieldContainer[User]
    delay: int
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., index: _Optional[int] = ..., shifts: _Optional[_Iterable[_Union[Shift, _Mapping]]] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., delay: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EscalationPolicy(_message.Message):
    __slots__ = ("id", "name", "steps", "customer", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    steps: _containers.RepeatedCompositeFieldContainer[EscalationStep]
    customer: Customer
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., steps: _Optional[_Iterable[_Union[EscalationStep, _Mapping]]] = ..., customer: _Optional[_Union[Customer, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ObjectsOfInterestRequest(_message.Message):
    __slots__ = ("id", "incident", "object_of_interests", "initiated_user", "cancelled", "timestamp", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_OF_INTERESTS_FIELD_NUMBER: _ClassVar[int]
    INITIATED_USER_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    incident: Incident
    object_of_interests: _containers.RepeatedCompositeFieldContainer[TrackedObject]
    initiated_user: User
    cancelled: bool
    timestamp: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., incident: _Optional[_Union[Incident, _Mapping]] = ..., object_of_interests: _Optional[_Iterable[_Union[TrackedObject, _Mapping]]] = ..., initiated_user: _Optional[_Union[User, _Mapping]] = ..., cancelled: bool = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ObjectOfInterestTrackingJob(_message.Message):
    __slots__ = ("id", "status", "tracking_requests", "start", "end", "matches", "created", "updated")
    class ObjectOfInterestTrackingJobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus]
        IN_PROGRESS: _ClassVar[ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus]
        COMPLETED: _ClassVar[ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus]
        TIMEOUT: _ClassVar[ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus]
    UNKNOWN: ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus
    IN_PROGRESS: ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus
    COMPLETED: ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus
    TIMEOUT: ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TRACKING_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus
    tracking_requests: _containers.RepeatedCompositeFieldContainer[ObjectsOfInterestRequest]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    matches: _containers.RepeatedCompositeFieldContainer[MatchPrediction]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[ObjectOfInterestTrackingJob.ObjectOfInterestTrackingJobStatus, str]] = ..., tracking_requests: _Optional[_Iterable[_Union[ObjectsOfInterestRequest, _Mapping]]] = ..., start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., matches: _Optional[_Iterable[_Union[MatchPrediction, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MatchPredictionAssignment(_message.Message):
    __slots__ = ("id", "assignee", "receipt", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    assignee: User
    receipt: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., assignee: _Optional[_Union[User, _Mapping]] = ..., receipt: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MatchPrediction(_message.Message):
    __slots__ = ("id", "object_track_id_in_target_frame", "target_frame", "confidence", "status", "tracked_object", "assignees", "distance", "time_diff", "decision_code", "created", "updated")
    class MatchPredictionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[MatchPrediction.MatchPredictionStatus]
        AUTO_CONFIRMED: _ClassVar[MatchPrediction.MatchPredictionStatus]
        UNCONFIRMED: _ClassVar[MatchPrediction.MatchPredictionStatus]
        CONFIRMED: _ClassVar[MatchPrediction.MatchPredictionStatus]
        REJECTED: _ClassVar[MatchPrediction.MatchPredictionStatus]
        TIMEOUT: _ClassVar[MatchPrediction.MatchPredictionStatus]
        UNSURE: _ClassVar[MatchPrediction.MatchPredictionStatus]
    UNKNOWN: MatchPrediction.MatchPredictionStatus
    AUTO_CONFIRMED: MatchPrediction.MatchPredictionStatus
    UNCONFIRMED: MatchPrediction.MatchPredictionStatus
    CONFIRMED: MatchPrediction.MatchPredictionStatus
    REJECTED: MatchPrediction.MatchPredictionStatus
    TIMEOUT: MatchPrediction.MatchPredictionStatus
    UNSURE: MatchPrediction.MatchPredictionStatus
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TRACK_ID_IN_TARGET_FRAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_FRAME_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TRACKED_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEES_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    TIME_DIFF_FIELD_NUMBER: _ClassVar[int]
    DECISION_CODE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_track_id_in_target_frame: str
    target_frame: _ai_models_pb2.InferenceFrame
    confidence: float
    status: MatchPrediction.MatchPredictionStatus
    tracked_object: TrackedObject
    assignees: _containers.RepeatedCompositeFieldContainer[MatchPredictionAssignment]
    distance: float
    time_diff: float
    decision_code: int
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., object_track_id_in_target_frame: _Optional[str] = ..., target_frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ..., confidence: _Optional[float] = ..., status: _Optional[_Union[MatchPrediction.MatchPredictionStatus, str]] = ..., tracked_object: _Optional[_Union[TrackedObject, _Mapping]] = ..., assignees: _Optional[_Iterable[_Union[MatchPredictionAssignment, _Mapping]]] = ..., distance: _Optional[float] = ..., time_diff: _Optional[float] = ..., decision_code: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TrackedObject(_message.Message):
    __slots__ = ("id", "global_id", "customer_id", "facility_id", "camera_id", "frame_id", "tracking_job_id", "detected_object", "timestamp", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    TRACKING_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    DETECTED_OBJECT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    global_id: str
    customer_id: str
    facility_id: str
    camera_id: str
    frame_id: str
    tracking_job_id: str
    detected_object: _ai_models_pb2.DetectedObject
    timestamp: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., global_id: _Optional[str] = ..., customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., camera_id: _Optional[str] = ..., frame_id: _Optional[str] = ..., tracking_job_id: _Optional[str] = ..., detected_object: _Optional[_Union[_ai_models_pb2.DetectedObject, _Mapping]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TrackedObjectList(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[TrackedObject]
    def __init__(self, objects: _Optional[_Iterable[_Union[TrackedObject, _Mapping]]] = ...) -> None: ...

class UnConfirmedPredictionRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: User
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class MatchPredictionList(_message.Message):
    __slots__ = ("predictions",)
    PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    predictions: _containers.RepeatedCompositeFieldContainer[MatchPrediction]
    def __init__(self, predictions: _Optional[_Iterable[_Union[MatchPrediction, _Mapping]]] = ...) -> None: ...

class DisableCameras(_message.Message):
    __slots__ = ("id", "duration", "cameras", "facility_snapshot", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    FACILITY_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    duration: int
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    facility_snapshot: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., duration: _Optional[int] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., facility_snapshot: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FacilityControl(_message.Message):
    __slots__ = ("id", "facility", "created", "updated", "completed", "disable_cameras", "enable_facility")
    ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    DISABLE_CAMERAS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    facility: Facility
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    completed: _timestamp_pb2.Timestamp
    disable_cameras: DisableCameras
    enable_facility: bool
    def __init__(self, id: _Optional[str] = ..., facility: _Optional[_Union[Facility, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., disable_cameras: _Optional[_Union[DisableCameras, _Mapping]] = ..., enable_facility: bool = ...) -> None: ...

class AuthorizedBadgeHolder(_message.Message):
    __slots__ = ("id", "name", "vendor_id", "badge_image_url", "customer", "first_seen", "last_seen", "created", "updated", "last_confirmed_frame", "string_tags")
    class StringTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    BADGE_IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    FIRST_SEEN_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    LAST_CONFIRMED_FRAME_FIELD_NUMBER: _ClassVar[int]
    STRING_TAGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    vendor_id: str
    badge_image_url: str
    customer: Customer
    first_seen: _timestamp_pb2.Timestamp
    last_seen: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    last_confirmed_frame: _ai_models_pb2.InferenceFrame
    string_tags: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., vendor_id: _Optional[str] = ..., badge_image_url: _Optional[str] = ..., customer: _Optional[_Union[Customer, _Mapping]] = ..., first_seen: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_seen: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_confirmed_frame: _Optional[_Union[_ai_models_pb2.InferenceFrame, _Mapping]] = ..., string_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class AccessControlEvent(_message.Message):
    __slots__ = ("id", "result", "authorized_badge_holder", "badge_reader", "confirmation_result", "validated_by", "string_tags")
    class BadgeReaderResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[AccessControlEvent.BadgeReaderResult]
        GRANTED: _ClassVar[AccessControlEvent.BadgeReaderResult]
        DENIED: _ClassVar[AccessControlEvent.BadgeReaderResult]
    UNKNOWN: AccessControlEvent.BadgeReaderResult
    GRANTED: AccessControlEvent.BadgeReaderResult
    DENIED: AccessControlEvent.BadgeReaderResult
    class ConfirmationResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_STATUS: _ClassVar[AccessControlEvent.ConfirmationResult]
        PENDING: _ClassVar[AccessControlEvent.ConfirmationResult]
        MISMATCHED: _ClassVar[AccessControlEvent.ConfirmationResult]
        CONFIRMED: _ClassVar[AccessControlEvent.ConfirmationResult]
        AUTO_CONFIRMED: _ClassVar[AccessControlEvent.ConfirmationResult]
    UNKNOWN_STATUS: AccessControlEvent.ConfirmationResult
    PENDING: AccessControlEvent.ConfirmationResult
    MISMATCHED: AccessControlEvent.ConfirmationResult
    CONFIRMED: AccessControlEvent.ConfirmationResult
    AUTO_CONFIRMED: AccessControlEvent.ConfirmationResult
    class StringTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZED_BADGE_HOLDER_FIELD_NUMBER: _ClassVar[int]
    BADGE_READER_FIELD_NUMBER: _ClassVar[int]
    CONFIRMATION_RESULT_FIELD_NUMBER: _ClassVar[int]
    VALIDATED_BY_FIELD_NUMBER: _ClassVar[int]
    STRING_TAGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    result: AccessControlEvent.BadgeReaderResult
    authorized_badge_holder: AuthorizedBadgeHolder
    badge_reader: BadgeReader
    confirmation_result: AccessControlEvent.ConfirmationResult
    validated_by: User
    string_tags: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., result: _Optional[_Union[AccessControlEvent.BadgeReaderResult, str]] = ..., authorized_badge_holder: _Optional[_Union[AuthorizedBadgeHolder, _Mapping]] = ..., badge_reader: _Optional[_Union[BadgeReader, _Mapping]] = ..., confirmation_result: _Optional[_Union[AccessControlEvent.ConfirmationResult, str]] = ..., validated_by: _Optional[_Union[User, _Mapping]] = ..., string_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class VapeDetectionEvent(_message.Message):
    __slots__ = ("id", "vape_detector", "string_tags")
    class StringTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    VAPE_DETECTOR_FIELD_NUMBER: _ClassVar[int]
    STRING_TAGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    vape_detector: VapeDetector
    string_tags: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., vape_detector: _Optional[_Union[VapeDetector, _Mapping]] = ..., string_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UserAssignment(_message.Message):
    __slots__ = ("id", "assignee", "receipt", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    RECEIPT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    assignee: User
    receipt: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., assignee: _Optional[_Union[User, _Mapping]] = ..., receipt: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SystemEvent(_message.Message):
    __slots__ = ("id", "timestamp", "created", "updated", "customer", "facility", "zone", "location", "description", "assignees", "cameras", "frames", "access_control_event", "vape_detection_event", "string_tags")
    class StringTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEES_FIELD_NUMBER: _ClassVar[int]
    CAMERAS_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    ACCESS_CONTROL_EVENT_FIELD_NUMBER: _ClassVar[int]
    VAPE_DETECTION_EVENT_FIELD_NUMBER: _ClassVar[int]
    STRING_TAGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    timestamp: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    customer: Customer
    facility: Facility
    zone: Zone
    location: Location
    description: str
    assignees: _containers.RepeatedCompositeFieldContainer[UserAssignment]
    cameras: _containers.RepeatedCompositeFieldContainer[Camera]
    frames: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.InferenceFrame]
    access_control_event: AccessControlEvent
    vape_detection_event: VapeDetectionEvent
    string_tags: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., customer: _Optional[_Union[Customer, _Mapping]] = ..., facility: _Optional[_Union[Facility, _Mapping]] = ..., zone: _Optional[_Union[Zone, _Mapping]] = ..., location: _Optional[_Union[Location, _Mapping]] = ..., description: _Optional[str] = ..., assignees: _Optional[_Iterable[_Union[UserAssignment, _Mapping]]] = ..., cameras: _Optional[_Iterable[_Union[Camera, _Mapping]]] = ..., frames: _Optional[_Iterable[_Union[_ai_models_pb2.InferenceFrame, _Mapping]]] = ..., access_control_event: _Optional[_Union[AccessControlEvent, _Mapping]] = ..., vape_detection_event: _Optional[_Union[VapeDetectionEvent, _Mapping]] = ..., string_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class SystemEventList(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[SystemEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[SystemEvent, _Mapping]]] = ...) -> None: ...

class InferenceFrameList(_message.Message):
    __slots__ = ("frames",)
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    frames: _containers.RepeatedCompositeFieldContainer[_ai_models_pb2.InferenceFrame]
    def __init__(self, frames: _Optional[_Iterable[_Union[_ai_models_pb2.InferenceFrame, _Mapping]]] = ...) -> None: ...
