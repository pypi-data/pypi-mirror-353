from typing import Optional, Callable, Dict
from queue import Queue
from collections import defaultdict
import threading
import json


from datetime import datetime

from kafka import KafkaConsumer

from .generated.models.service_models_pb2 import VideoIngestFragment

from .utils.logging import logger
from .utils.metric_utils import VideoIngestFragmentMetric


class KafkaConsumerClient(threading.Thread):

    @staticmethod
    def _deserialize_message(m: bytes):
        """
        Attempts to deserialize the message:
        1. First, tries to decode the bytes into a JSON object.
        2. If JSON decoding fails, assumes the bytes represent a Protobuf message (VideoIngestFragment)
            and parses it accordingly.
        """
        try:
            # Try to decode the message as JSON.
            return json.loads(m.decode('utf-8'))
        except Exception as json_error:
            # If JSON decoding fails, try deserializing as a Protobuf message.
            try:
                message = VideoIngestFragment()
                message.ParseFromString(m)
                return message
            except Exception as pb_error:
                raise ValueError(f"Failed to deserialize message as JSON or Protobuf: JSON error: {json_error}, Protobuf error: {pb_error}")

    def __init__(
        self,

        topic: str,
        bootstrap_servers: str,
        group_id: str,
        on_new_key: Callable[[str], Queue],
        on_client_stop: Optional[Callable[[], None]] = None,
        index: int = 0,
        metrics_queue: Optional[Queue] = None,
        drop_latency_threshold: float = 100000.0,
    ):
        super().__init__(daemon=True, name=f"kafka_consumer_client_{index}")
        self.index = index
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self._metrics_queue = metrics_queue
        self._drop_latency_threshold = drop_latency_threshold
        self._on_client_stop = on_client_stop or (lambda: None)

        self.key_queue_map: Dict[str, Queue] = {}

        logger.info(f"Creating KafkaConsumerClient for topic: {topic}, group_id: {group_id}, bootstrap_servers: {bootstrap_servers}")

        self.consumer = KafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
            key_deserializer=lambda k: k.decode('utf-8') if isinstance(k, bytes) else k,
            value_deserializer=self._deserialize_message,
        )

        self._on_new_key = on_new_key
        self._stop_event = threading.Event()

        self.msg_count: defaultdict = defaultdict(int)

        self.kafka_consume_age_metrics: Dict[str, VideoIngestFragmentMetric] = {}

        self._metrics_task_thread = threading.Thread(
            target=self._metrics_task,
            daemon=True,
            name=f"kafka_consumer_metrics_{index}"
        )

    def _metrics_task(self):

        while not self._stop_event.is_set():
            try:
                self._stop_event.wait(60)

                for key, metric in self.kafka_consume_age_metrics.items():
                    logger.debug(metric)

                    if metric.threshold_exceeded(self._drop_latency_threshold):
                        logger.warning(f"[{key}] {metric}")

                    if self._metrics_queue:
                        self._metrics_queue.put(metric)

            except Exception as e:
                logger.error(f"Error in metrics task: {e}")

    def get_input_queue(self, key: str) -> Optional[Queue]:
        """
        Callback invoked by the KafkaConsumerPool when a new key (e.g. camera ID) is encountered.
        It creates a new decoding pipeline (with its own input queue) if one does not already exist.
        If a pipeline already exists, it returns the existing input queue.

        NOTE: No locking for this operation as kafka will guaranty thread safety.
        This consumer will consume messages for a set of keys (partition) and this messages are consumed
        in a single thread and in order.

        """

        input_queue = self.key_queue_map.get(key)

        if not input_queue:
            input_queue = self._on_new_key(key)
            self.kafka_consume_age_metrics[key] = VideoIngestFragmentMetric(key, "kafka_consume_age")
            if input_queue:
                self.key_queue_map[key] = input_queue
        return input_queue

    def run(self):

        self._metrics_task_thread.start()

        for message in self.consumer:
            if self._stop_event.is_set():
                break

            key = message.key

            message_timestamp = message.value.start_ts.ToDatetime()
            frame_age = (datetime.utcnow() - message_timestamp).total_seconds()
            if frame_age > self._drop_latency_threshold:
                logger.warning(f"[{key}] Message Age: {frame_age:.2f} seconds. Dropping!!!")
                continue

            self.msg_count[key] += 1

            queue = self.get_input_queue(key)
            if not queue:
                continue
            queue.put_nowait(message.value)
            logger.debug(f"[{self.index}] Enqued message for key: {key}")
            self.kafka_consume_age_metrics[key].append(frame_age)

        self._on_client_stop()

    def stop(self):

        self._stop_event.set()
        self._metrics_task_thread.join(timeout=5)
        self.consumer.close()
        logger.info("KafkaConsumerClient stopped.")
