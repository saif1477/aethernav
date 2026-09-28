"""Transparent planar inertial baseline."""
from __future__ import annotations

import numpy as np
import pandas as pd


def integrate_planar_inertial(frame: pd.DataFrame) -> np.ndarray:
    """Integrate forward acceleration and yaw rate in a local EN frame.

    Assumptions are explicit: accelerometer X is forward specific force after
    gravity compensation, gyroscope Z is yaw rate, and the first GNSS speed/heading
    initialize the state. The bundled sample satisfies this contract; real IO-VNBD
    axis conventions must be mapped before using this baseline.
    """
    required = {"timestamp", "accelerometer_x", "gyroscope_z"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"inertial baseline requires columns: {sorted(missing)}")
    t = frame.timestamp.to_numpy(float)
    ax = frame.accelerometer_x.to_numpy(float)
    yaw_rate = frame.gyroscope_z.to_numpy(float)
    speed0 = float(frame.speed_mps.dropna().iloc[0]) if "speed_mps" in frame and frame.speed_mps.notna().any() else 0.0
    heading0 = float(frame.heading_deg.dropna().iloc[0]) if "heading_deg" in frame and frame.heading_deg.notna().any() else 0.0
    state = np.zeros((len(frame), 4), dtype=float)  # east, north, speed, heading radians
    state[0, 2] = speed0
    state[0, 3] = np.radians(heading0)
    for i in range(1, len(frame)):
        dt = max(0.0, t[i] - t[i - 1])
        state[i, 2] = state[i - 1, 2] + ax[i - 1] * dt
        state[i, 3] = state[i - 1, 3] + yaw_rate[i - 1] * dt
        state[i, 0] = state[i - 1, 0] + state[i, 2] * np.sin(state[i, 3]) * dt
        state[i, 1] = state[i - 1, 1] + state[i, 2] * np.cos(state[i, 3]) * dt
    return state
