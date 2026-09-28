"""Canonical sensor data contracts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = ("timestamp",)
OPTIONAL_COLUMNS = (
    "sequence_id", "latitude", "longitude", "altitude_m", "speed_mps", "heading_deg",
    "accelerometer_x", "accelerometer_y", "accelerometer_z",
    "gyroscope_x", "gyroscope_y", "gyroscope_z",
    "magnetometer_x", "magnetometer_y", "magnetometer_z",
)


@dataclass(frozen=True)
class DatasetReport:
    rows: int
    columns: list[str]
    sequences: int
    timestamp_monotonic: bool
    duplicate_timestamps: int
    missing_values: dict[str, int]
    sampling_rate_hz: float | None
    coordinate_bounds: dict[str, float] | None
    warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def canonicalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize common source aliases without inventing absent measurements."""
    aliases = {
        "time": "timestamp", "ts": "timestamp", "lat": "latitude", "lon": "longitude",
        "lng": "longitude", "alt": "altitude_m", "speed": "speed_mps",
        "accel_x": "accelerometer_x", "accel_y": "accelerometer_y", "accel_z": "accelerometer_z",
        "gyro_x": "gyroscope_x", "gyro_y": "gyroscope_y", "gyro_z": "gyroscope_z",
    }
    renamed = frame.rename(columns={c: aliases.get(str(c).strip().lower(), str(c).strip().lower()) for c in frame.columns})
    if "timestamp" not in renamed:
        raise ValueError("Dataset must contain a timestamp column (accepted aliases: time, ts)")
    renamed["timestamp"] = pd.to_numeric(renamed["timestamp"], errors="coerce")
    return renamed
