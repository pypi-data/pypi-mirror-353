from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from models import graph_models_pb2 as _graph_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IncidentsAvgResolveTimeRequest(_message.Message):
    __slots__ = ("facilities", "customer", "from_timestamp", "to_timestamp")
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    facilities: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Facility]
    customer: _graph_models_pb2.Customer
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, facilities: _Optional[_Iterable[_Union[_graph_models_pb2.Facility, _Mapping]]] = ..., customer: _Optional[_Union[_graph_models_pb2.Customer, _Mapping]] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IncidentsAvgResolveTimeResponse(_message.Message):
    __slots__ = ("avg", "closed_incidents_count")
    AVG_FIELD_NUMBER: _ClassVar[int]
    CLOSED_INCIDENTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    avg: float
    closed_incidents_count: int
    def __init__(self, avg: _Optional[float] = ..., closed_incidents_count: _Optional[int] = ...) -> None: ...

class IncidentsHistogramRequest(_message.Message):
    __slots__ = ("facilities", "customer", "from_timestamp", "to_timestamp", "after_key", "max_buckets")
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AFTER_KEY_FIELD_NUMBER: _ClassVar[int]
    MAX_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    facilities: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Facility]
    customer: _graph_models_pb2.Customer
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    after_key: IncidentsHistogramResponse.Bucket.Key
    max_buckets: int
    def __init__(self, facilities: _Optional[_Iterable[_Union[_graph_models_pb2.Facility, _Mapping]]] = ..., customer: _Optional[_Union[_graph_models_pb2.Customer, _Mapping]] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., after_key: _Optional[_Union[IncidentsHistogramResponse.Bucket.Key, _Mapping]] = ..., max_buckets: _Optional[int] = ...) -> None: ...

class IncidentsHistogramResponse(_message.Message):
    __slots__ = ("after_key", "buckets")
    class Bucket(_message.Message):
        __slots__ = ("key", "count")
        class Key(_message.Message):
            __slots__ = ("date", "trigger_rule_id", "facility_id")
            DATE_FIELD_NUMBER: _ClassVar[int]
            TRIGGER_RULE_ID_FIELD_NUMBER: _ClassVar[int]
            FACILITY_ID_FIELD_NUMBER: _ClassVar[int]
            date: str
            trigger_rule_id: str
            facility_id: str
            def __init__(self, date: _Optional[str] = ..., trigger_rule_id: _Optional[str] = ..., facility_id: _Optional[str] = ...) -> None: ...
        KEY_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        key: IncidentsHistogramResponse.Bucket.Key
        count: int
        def __init__(self, key: _Optional[_Union[IncidentsHistogramResponse.Bucket.Key, _Mapping]] = ..., count: _Optional[int] = ...) -> None: ...
    AFTER_KEY_FIELD_NUMBER: _ClassVar[int]
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    after_key: IncidentsHistogramResponse.Bucket.Key
    buckets: _containers.RepeatedCompositeFieldContainer[IncidentsHistogramResponse.Bucket]
    def __init__(self, after_key: _Optional[_Union[IncidentsHistogramResponse.Bucket.Key, _Mapping]] = ..., buckets: _Optional[_Iterable[_Union[IncidentsHistogramResponse.Bucket, _Mapping]]] = ...) -> None: ...

class IncidentsOverviewRequest(_message.Message):
    __slots__ = ("facilities", "customer", "from_timestamp", "to_timestamp")
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    facilities: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Facility]
    customer: _graph_models_pb2.Customer
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, facilities: _Optional[_Iterable[_Union[_graph_models_pb2.Facility, _Mapping]]] = ..., customer: _Optional[_Union[_graph_models_pb2.Customer, _Mapping]] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IncidentsOverviewResponse(_message.Message):
    __slots__ = ("open_incidents_total_count", "open_incidents")
    OPEN_INCIDENTS_TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    OPEN_INCIDENTS_FIELD_NUMBER: _ClassVar[int]
    open_incidents_total_count: int
    open_incidents: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Incident]
    def __init__(self, open_incidents_total_count: _Optional[int] = ..., open_incidents: _Optional[_Iterable[_Union[_graph_models_pb2.Incident, _Mapping]]] = ...) -> None: ...

class OccupancyHistogramRequest(_message.Message):
    __slots__ = ("facility", "level", "location", "camera", "from_timestamp", "to_timestamp")
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    CAMERA_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    facility: _graph_models_pb2.Facility
    level: _graph_models_pb2.Level
    location: _graph_models_pb2.Location
    camera: _graph_models_pb2.Camera
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, facility: _Optional[_Union[_graph_models_pb2.Facility, _Mapping]] = ..., level: _Optional[_Union[_graph_models_pb2.Level, _Mapping]] = ..., location: _Optional[_Union[_graph_models_pb2.Location, _Mapping]] = ..., camera: _Optional[_Union[_graph_models_pb2.Camera, _Mapping]] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OccupancyHistogramResponse(_message.Message):
    __slots__ = ("buckets",)
    class Bucket(_message.Message):
        __slots__ = ("timestamp", "count")
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        timestamp: _timestamp_pb2.Timestamp
        count: int
        def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., count: _Optional[int] = ...) -> None: ...
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    buckets: _containers.RepeatedCompositeFieldContainer[OccupancyHistogramResponse.Bucket]
    def __init__(self, buckets: _Optional[_Iterable[_Union[OccupancyHistogramResponse.Bucket, _Mapping]]] = ...) -> None: ...

class OccupancyHistogramByZoneTypeRequest(_message.Message):
    __slots__ = ("facility", "zone_types", "from_timestamp", "to_timestamp")
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    ZONE_TYPES_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    facility: _graph_models_pb2.Facility
    zone_types: _containers.RepeatedScalarFieldContainer[_graph_models_pb2.Zone.ZoneType]
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, facility: _Optional[_Union[_graph_models_pb2.Facility, _Mapping]] = ..., zone_types: _Optional[_Iterable[_Union[_graph_models_pb2.Zone.ZoneType, str]]] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AnalyticsReportRequest(_message.Message):
    __slots__ = ("id", "user", "facilities", "email_override", "from_timestamp", "to_timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    FACILITIES_FIELD_NUMBER: _ClassVar[int]
    EMAIL_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    user: _graph_models_pb2.User
    facilities: _containers.RepeatedCompositeFieldContainer[_graph_models_pb2.Facility]
    email_override: str
    from_timestamp: _timestamp_pb2.Timestamp
    to_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., user: _Optional[_Union[_graph_models_pb2.User, _Mapping]] = ..., facilities: _Optional[_Iterable[_Union[_graph_models_pb2.Facility, _Mapping]]] = ..., email_override: _Optional[str] = ..., from_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
