from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MLModel(_message.Message):
    __slots__ = ("id", "name", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    version: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class InferenceFrame(_message.Message):
    __slots__ = ("id", "camera_id", "customer_id", "facility_id", "width", "height", "timestamp", "objects", "bucket", "key", "string_tags", "numeric_tags", "url", "rotation", "models", "codec", "embeddings", "created", "updated")
    class Codec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[InferenceFrame.Codec]
        H264: _ClassVar[InferenceFrame.Codec]
        H265: _ClassVar[InferenceFrame.Codec]
    UNKNOWN: InferenceFrame.Codec
    H264: InferenceFrame.Codec
    H265: InferenceFrame.Codec
    class StringTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class NumericTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    STRING_TAGS_FIELD_NUMBER: _ClassVar[int]
    NUMERIC_TAGS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    CODEC_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    camera_id: str
    customer_id: str
    facility_id: str
    width: int
    height: int
    timestamp: _timestamp_pb2.Timestamp
    objects: _containers.RepeatedCompositeFieldContainer[DetectedObject]
    bucket: str
    key: str
    string_tags: _containers.ScalarMap[str, str]
    numeric_tags: _containers.ScalarMap[str, float]
    url: str
    rotation: int
    models: _containers.RepeatedCompositeFieldContainer[MLModel]
    codec: InferenceFrame.Codec
    embeddings: Embedding
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., camera_id: _Optional[str] = ..., customer_id: _Optional[str] = ..., facility_id: _Optional[str] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., objects: _Optional[_Iterable[_Union[DetectedObject, _Mapping]]] = ..., bucket: _Optional[str] = ..., key: _Optional[str] = ..., string_tags: _Optional[_Mapping[str, str]] = ..., numeric_tags: _Optional[_Mapping[str, float]] = ..., url: _Optional[str] = ..., rotation: _Optional[int] = ..., models: _Optional[_Iterable[_Union[MLModel, _Mapping]]] = ..., codec: _Optional[_Union[InferenceFrame.Codec, str]] = ..., embeddings: _Optional[_Union[Embedding, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DetectedObject(_message.Message):
    __slots__ = ("id", "object_class", "confidence", "x_min", "y_min", "x_max", "y_max", "track_id", "global_track_id", "highlighted", "human_poses", "embeddings", "label", "person", "reid_embeddings", "position_x", "position_y", "orientation", "string_tags", "numeric_tags", "created", "updated")
    class ObjectClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[DetectedObject.ObjectClass]
        PERSON: _ClassVar[DetectedObject.ObjectClass]
        WEAPON: _ClassVar[DetectedObject.ObjectClass]
        CAR: _ClassVar[DetectedObject.ObjectClass]
        LONG_GUN: _ClassVar[DetectedObject.ObjectClass]
        PHONE: _ClassVar[DetectedObject.ObjectClass]
        BACKPACK: _ClassVar[DetectedObject.ObjectClass]
        SUITCASE: _ClassVar[DetectedObject.ObjectClass]
        BASEBALL_BAT: _ClassVar[DetectedObject.ObjectClass]
        KNIFE: _ClassVar[DetectedObject.ObjectClass]
        FORKLIFT: _ClassVar[DetectedObject.ObjectClass]
    UNKNOWN: DetectedObject.ObjectClass
    PERSON: DetectedObject.ObjectClass
    WEAPON: DetectedObject.ObjectClass
    CAR: DetectedObject.ObjectClass
    LONG_GUN: DetectedObject.ObjectClass
    PHONE: DetectedObject.ObjectClass
    BACKPACK: DetectedObject.ObjectClass
    SUITCASE: DetectedObject.ObjectClass
    BASEBALL_BAT: DetectedObject.ObjectClass
    KNIFE: DetectedObject.ObjectClass
    FORKLIFT: DetectedObject.ObjectClass
    class StringTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class NumericTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    X_MIN_FIELD_NUMBER: _ClassVar[int]
    Y_MIN_FIELD_NUMBER: _ClassVar[int]
    X_MAX_FIELD_NUMBER: _ClassVar[int]
    Y_MAX_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTED_FIELD_NUMBER: _ClassVar[int]
    HUMAN_POSES_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PERSON_FIELD_NUMBER: _ClassVar[int]
    REID_EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    POSITION_X_FIELD_NUMBER: _ClassVar[int]
    POSITION_Y_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    STRING_TAGS_FIELD_NUMBER: _ClassVar[int]
    NUMERIC_TAGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_class: DetectedObject.ObjectClass
    confidence: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    track_id: str
    global_track_id: str
    highlighted: bool
    human_poses: HumanPose
    embeddings: Embedding
    label: str
    person: Person
    reid_embeddings: Embedding
    position_x: float
    position_y: float
    orientation: float
    string_tags: _containers.ScalarMap[str, str]
    numeric_tags: _containers.ScalarMap[str, float]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., object_class: _Optional[_Union[DetectedObject.ObjectClass, str]] = ..., confidence: _Optional[float] = ..., x_min: _Optional[float] = ..., y_min: _Optional[float] = ..., x_max: _Optional[float] = ..., y_max: _Optional[float] = ..., track_id: _Optional[str] = ..., global_track_id: _Optional[str] = ..., highlighted: bool = ..., human_poses: _Optional[_Union[HumanPose, _Mapping]] = ..., embeddings: _Optional[_Union[Embedding, _Mapping]] = ..., label: _Optional[str] = ..., person: _Optional[_Union[Person, _Mapping]] = ..., reid_embeddings: _Optional[_Union[Embedding, _Mapping]] = ..., position_x: _Optional[float] = ..., position_y: _Optional[float] = ..., orientation: _Optional[float] = ..., string_tags: _Optional[_Mapping[str, str]] = ..., numeric_tags: _Optional[_Mapping[str, float]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class HumanPose(_message.Message):
    __slots__ = ("id", "confidence", "body_parts")
    class BodyPart(_message.Message):
        __slots__ = ("name", "pos_x", "pos_y", "confidence", "id")
        class KeyPoint(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN: _ClassVar[HumanPose.BodyPart.KeyPoint]
            NOSE: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_EYE: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_EYE: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_EAR: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_EAR: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_SHOULDER: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_SHOULDER: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_ELBOW: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_ELBOW: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_WRIST: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_WRIST: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_HIP: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_HIP: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_KNEE: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_KNEE: _ClassVar[HumanPose.BodyPart.KeyPoint]
            LEFT_ANKLE: _ClassVar[HumanPose.BodyPart.KeyPoint]
            RIGHT_ANKLE: _ClassVar[HumanPose.BodyPart.KeyPoint]
        UNKNOWN: HumanPose.BodyPart.KeyPoint
        NOSE: HumanPose.BodyPart.KeyPoint
        LEFT_EYE: HumanPose.BodyPart.KeyPoint
        RIGHT_EYE: HumanPose.BodyPart.KeyPoint
        LEFT_EAR: HumanPose.BodyPart.KeyPoint
        RIGHT_EAR: HumanPose.BodyPart.KeyPoint
        LEFT_SHOULDER: HumanPose.BodyPart.KeyPoint
        RIGHT_SHOULDER: HumanPose.BodyPart.KeyPoint
        LEFT_ELBOW: HumanPose.BodyPart.KeyPoint
        RIGHT_ELBOW: HumanPose.BodyPart.KeyPoint
        LEFT_WRIST: HumanPose.BodyPart.KeyPoint
        RIGHT_WRIST: HumanPose.BodyPart.KeyPoint
        LEFT_HIP: HumanPose.BodyPart.KeyPoint
        RIGHT_HIP: HumanPose.BodyPart.KeyPoint
        LEFT_KNEE: HumanPose.BodyPart.KeyPoint
        RIGHT_KNEE: HumanPose.BodyPart.KeyPoint
        LEFT_ANKLE: HumanPose.BodyPart.KeyPoint
        RIGHT_ANKLE: HumanPose.BodyPart.KeyPoint
        NAME_FIELD_NUMBER: _ClassVar[int]
        POS_X_FIELD_NUMBER: _ClassVar[int]
        POS_Y_FIELD_NUMBER: _ClassVar[int]
        CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        name: HumanPose.BodyPart.KeyPoint
        pos_x: float
        pos_y: float
        confidence: float
        id: str
        def __init__(self, name: _Optional[_Union[HumanPose.BodyPart.KeyPoint, str]] = ..., pos_x: _Optional[float] = ..., pos_y: _Optional[float] = ..., confidence: _Optional[float] = ..., id: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    BODY_PARTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    confidence: float
    body_parts: _containers.RepeatedCompositeFieldContainer[HumanPose.BodyPart]
    def __init__(self, id: _Optional[str] = ..., confidence: _Optional[float] = ..., body_parts: _Optional[_Iterable[_Union[HumanPose.BodyPart, _Mapping]]] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ("id", "embedding")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_FIELD_NUMBER: _ClassVar[int]
    id: str
    embedding: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, id: _Optional[str] = ..., embedding: _Optional[_Iterable[float]] = ...) -> None: ...

class Tracker(_message.Message):
    __slots__ = ("id", "tracker_id", "mode")
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Tracker.Mode]
        ACTIVE: _ClassVar[Tracker.Mode]
        TENTATIVE: _ClassVar[Tracker.Mode]
        INACTIVE: _ClassVar[Tracker.Mode]
        TERMINATED: _ClassVar[Tracker.Mode]
    UNKNOWN: Tracker.Mode
    ACTIVE: Tracker.Mode
    TENTATIVE: Tracker.Mode
    INACTIVE: Tracker.Mode
    TERMINATED: Tracker.Mode
    ID_FIELD_NUMBER: _ClassVar[int]
    TRACKER_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    id: str
    tracker_id: int
    mode: Tracker.Mode
    def __init__(self, id: _Optional[str] = ..., tracker_id: _Optional[int] = ..., mode: _Optional[_Union[Tracker.Mode, str]] = ...) -> None: ...

class PositionDetails(_message.Message):
    __slots__ = ("id", "state", "confidence")
    class PositionState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[PositionDetails.PositionState]
        FALLEN: _ClassVar[PositionDetails.PositionState]
        STANDING: _ClassVar[PositionDetails.PositionState]
        SITTING: _ClassVar[PositionDetails.PositionState]
        WORKING_OUT: _ClassVar[PositionDetails.PositionState]
        HANDS_UP: _ClassVar[PositionDetails.PositionState]
        FIGHTING: _ClassVar[PositionDetails.PositionState]
        WALKING: _ClassVar[PositionDetails.PositionState]
    UNKNOWN: PositionDetails.PositionState
    FALLEN: PositionDetails.PositionState
    STANDING: PositionDetails.PositionState
    SITTING: PositionDetails.PositionState
    WORKING_OUT: PositionDetails.PositionState
    HANDS_UP: PositionDetails.PositionState
    FIGHTING: PositionDetails.PositionState
    WALKING: PositionDetails.PositionState
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: PositionDetails.PositionState
    confidence: float
    def __init__(self, id: _Optional[str] = ..., state: _Optional[_Union[PositionDetails.PositionState, str]] = ..., confidence: _Optional[float] = ...) -> None: ...

class Person(_message.Message):
    __slots__ = ("id", "position")
    ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    id: str
    position: PositionDetails
    def __init__(self, id: _Optional[str] = ..., position: _Optional[_Union[PositionDetails, _Mapping]] = ...) -> None: ...

class DetectedObjectList(_message.Message):
    __slots__ = ("id", "objects")
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    objects: _containers.RepeatedCompositeFieldContainer[DetectedObject]
    def __init__(self, id: _Optional[str] = ..., objects: _Optional[_Iterable[_Union[DetectedObject, _Mapping]]] = ...) -> None: ...
