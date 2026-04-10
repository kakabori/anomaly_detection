from datetime import datetime, timedelta
from typing import Protocol

from domain.model import SensorSnapshot


class AnomalyDetector(Protocol):
    def run(self, features) -> list[float]: ...


class FeatureExtractor(Protocol):
    window_width: timedelta

    def run(
        self, sensor_snapshots: list[SensorSnapshot]
    ) -> tuple[dict[str, list[float]], list[datetime], list[list[str]], list]: ...
