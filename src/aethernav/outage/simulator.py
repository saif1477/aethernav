"""Deterministic GNSS outage and degradation simulation."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OutageConfig:
    start_s: float
    end_s: float
    noise_std_m: float = 0.0
    seed: int = 2026
    recovery_s: float = 0.0


def simulate_gnss_outage(frame: pd.DataFrame, config: OutageConfig) -> pd.DataFrame:
    """Return a copy with GNSS masked during the configured interval.

    The original columns are retained and `gnss_available`, `gnss_degraded`, and
    `outage_phase` make the simulation auditable. Noise is applied only to available
    GNSS coordinates and is expressed approximately in metres (ENU perturbation).
    """
    if config.end_s <= config.start_s:
        raise ValueError("outage end must be greater than outage start")
    if "timestamp" not in frame:
        raise ValueError("timestamp is required")
    result = frame.copy()
    t = pd.to_numeric(result["timestamp"], errors="coerce").to_numpy(float)
    if np.isnan(t).any():
        raise ValueError("timestamps must be numeric before outage simulation")
    outage = (t >= config.start_s) & (t < config.end_s)
    recovery = (t >= config.end_s) & (t < config.end_s + config.recovery_s)
    result["gnss_available"] = ~outage
    result["gnss_degraded"] = recovery
    result["outage_phase"] = np.where(outage, "outage", np.where(recovery, "recovery", "normal"))
    for column in ("latitude", "longitude", "altitude_m", "speed_mps", "heading_deg"):
        if column in result:
            result.loc[outage, column] = np.nan
    if config.noise_std_m and {"latitude", "longitude"}.issubset(result):
        rng = np.random.default_rng(config.seed)
        earth_m_per_deg_lat = 111_132.0
        earth_m_per_deg_lon = 111_320.0 * np.cos(np.radians(result["latitude"].fillna(0.0)))
        normal = ~outage
        result.loc[normal, "latitude"] += rng.normal(0, config.noise_std_m, normal.sum()) / earth_m_per_deg_lat
        result.loc[normal, "longitude"] += rng.normal(0, config.noise_std_m, normal.sum()) / earth_m_per_deg_lon[normal]
    return result
