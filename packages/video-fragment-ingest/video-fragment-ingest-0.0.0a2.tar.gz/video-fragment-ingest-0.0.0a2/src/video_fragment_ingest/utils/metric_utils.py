from typing import List, Dict, Union

from collections import defaultdict, deque
import threading

import numpy as np


class VideoIngestFragmentMetric:
    def __init__(self, key: str, name: str, max_items: int = 1000):
        self.key = key
        self.name = name
        self._records: deque[float] = deque(maxlen=max_items)
        self._lock = threading.Lock()

    def append(self, value: float):
        if isinstance(value, (int, float)):
            with self._lock:
                self._records.append(float(value))

    def get_stats(self) -> Dict[str, float]:
        with self._lock:
            if not self._records:
                return {"avg": 0.0, "p99": 0.0}
            return {
                "avg": float(np.mean(self._records)),
                "p99": float(np.percentile(self._records, 99)),
            }

    def get_avg(self) -> float:
        with self._lock:
            return float(np.mean(self._records)) if self._records else 0.0

    def get_percentile(self, percentile: float) -> float:
        with self._lock:
            return float(np.percentile(self._records, percentile)) if self._records else 0.0

    def threshold_exceeded(self, threshold: float) -> bool:
        with self._lock:
            if not self._records:
                return False
            return float(np.mean(self._records)) > threshold

    def __str__(self):
        stats = self.get_stats()
        return f"[{self.key}] {self.name}: avg: {stats['avg']}, p99: {stats['p99']}"


def consolidate_metrics(
    records: List[Dict[str, Dict[str, Union[float, Dict[str, float]]]]]
) -> Dict[str, Dict[str, Dict[str, float]]]:
    result = defaultdict(lambda: defaultdict(list))

    for record in records:
        for stream_id, metrics in record.items():
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    result[stream_id][metric].append(float(value))
                # ignore dicts like {"avg": ..., "p99": ...}

    consolidated = {}
    for stream_id, metrics in result.items():
        consolidated[stream_id] = {}
        for metric, values in metrics.items():
            consolidated[stream_id][metric] = {
                "avg": round(float(np.mean(values)), 2),
                "p99": round(float(np.percentile(values, 99)), 2)
            }

    return consolidated
