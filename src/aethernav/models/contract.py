"""Canonical model contract shared by export tooling and mobile metadata."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class ModelContract:
    model_name: str = "aethernav_temporal_dead_reckoner"
    model_version: str = "integration-test-0"
    status: str = "integration-test"
    is_trained: bool = False
    preprocessing_version: str = "imu-v1"
    input_names: tuple[str, ...] = ("imu_window",)
    input_shape: tuple[int, ...] = (1, 20, 6)
    input_dtype: str = "float32"
    sampling_rate_hz: int = 20
    temporal_window_length: int = 20
    feature_order: tuple[str, ...] = (
        "accelerometer_x", "accelerometer_y", "accelerometer_z",
        "gyroscope_x", "gyroscope_y", "gyroscope_z",
    )
    normalization_mean: tuple[float, ...] = (0.0, 0.0, 9.80665, 0.0, 0.0, 0.0)
    normalization_std: tuple[float, ...] = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    coordinate_convention: str = "local_enu"
    output_names: tuple[str, ...] = ("motion_output",)
    output_shape: tuple[int, ...] = (1, 6)
    output_dtype: str = "float32"
    output_units: tuple[str, ...] = ("delta_east_m", "delta_north_m", "yaw_rate_correction_rad_s", "log_variance_east", "log_variance_north", "log_variance_yaw")
    uncertainty_representation: str = "log_variance"

    def as_dict(self) -> dict:
        data = asdict(self)
        for key in ("input_names", "input_shape", "feature_order", "normalization_mean", "normalization_std", "output_names", "output_shape", "output_units"):
            data[key] = list(data[key])
        return data


def write_contract(path: str | Path) -> Path:
    output = Path(path); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(ModelContract().as_dict(), indent=2) + "\n", encoding="utf-8"); return output
