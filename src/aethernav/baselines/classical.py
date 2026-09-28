"""Classical GNSS and vehicle-motion baselines."""
from __future__ import annotations

import numpy as np
import pandas as pd


def gnss_only_trajectory(frame: pd.DataFrame, reference_origin: tuple[float, float, float], enu_converter) -> np.ndarray:
    """Use GNSS when available and hold the last valid position through an outage."""
    valid = frame.get("gnss_available", pd.Series(True, index=frame.index)).to_numpy(bool)
    lat = frame.latitude.to_numpy(float); lon = frame.longitude.to_numpy(float)
    alt = frame.get("altitude_m", pd.Series(0.0, index=frame.index)).to_numpy(float)
    result = np.full((len(frame), 3), np.nan); last = np.zeros(3)
    for i in range(len(frame)):
        if valid[i] and np.isfinite([lat[i], lon[i], alt[i]]).all():
            last = enu_converter([lat[i]], [lon[i]], [alt[i]], reference_origin)[0]
        result[i] = last
    return result


def last_velocity_trajectory(frame: pd.DataFrame) -> np.ndarray:
    """Propagate the last known speed and heading in the local ENU plane."""
    t = frame.timestamp.to_numpy(float); speed = frame.speed_mps.to_numpy(float) if "speed_mps" in frame else np.zeros(len(frame))
    heading = frame.heading_deg.to_numpy(float) if "heading_deg" in frame else np.zeros(len(frame))
    valid = frame.get("gnss_available", pd.Series(True, index=frame.index)).to_numpy(bool)
    state = np.zeros((len(frame), 3)); v = float(speed[0]) if np.isfinite(speed[0]) else 0.0; h = float(heading[0]) if np.isfinite(heading[0]) else 0.0
    for i in range(1, len(frame)):
        dt = max(0.0, t[i] - t[i - 1])
        if valid[i] and np.isfinite(speed[i]): v = float(speed[i])
        if valid[i] and np.isfinite(heading[i]): h = float(heading[i])
        state[i, 0] = state[i - 1, 0] + v * np.sin(np.radians(h)) * dt
        state[i, 1] = state[i - 1, 1] + v * np.cos(np.radians(h)) * dt
        state[i, 2] = v
    return state


def ekf_trajectory(frame: pd.DataFrame, reference_origin: tuple[float, float, float], enu_converter, process_var=0.8, measurement_var=9.0) -> np.ndarray:
    """Small planar EKF with acceleration/yaw-rate propagation and GNSS position updates."""
    t = frame.timestamp.to_numpy(float); n = len(frame); x = np.zeros(4); P = np.eye(4) * 1.0
    imu = frame.accelerometer_x.to_numpy(float); gyro = frame.gyroscope_z.to_numpy(float)
    gnss = gnss_only_trajectory(frame, reference_origin, enu_converter); available = frame.get("gnss_available", pd.Series(True, index=frame.index)).to_numpy(bool)
    out = np.zeros((n, 3));
    if "speed_mps" in frame and np.isfinite(frame.speed_mps.iloc[0]): x[2] = frame.speed_mps.iloc[0]
    if "heading_deg" in frame and np.isfinite(frame.heading_deg.iloc[0]): x[3] = np.radians(frame.heading_deg.iloc[0])
    for i in range(n):
        if i:
            dt = max(1e-6, t[i] - t[i - 1]); a = imu[i - 1]; w = gyro[i - 1]
            x[0] += x[2] * np.sin(x[3]) * dt; x[1] += x[2] * np.cos(x[3]) * dt; x[2] += a * dt; x[3] += w * dt
            P += np.eye(4) * process_var * dt
        if available[i] and np.isfinite(gnss[i, :2]).all():
            H = np.zeros((2, 4)); H[:, :2] = np.eye(2); R = np.eye(2) * measurement_var
            innovation = gnss[i, :2] - x[:2]; S = H @ P @ H.T + R; K = P @ H.T @ np.linalg.inv(S); x += K @ innovation; P = (np.eye(4) - K @ H) @ P
        out[i] = (x[0], x[1], x[2])
    return out
