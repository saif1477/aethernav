"""FastAPI development and container API server for AetherNav."""
from __future__ import annotations

import json
from typing import Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from aethernav.schemas import canonicalize_frame
from aethernav.datasets.validation import validate_frame
from aethernav.baselines.classical import gnss_only_trajectory, last_velocity_trajectory, ekf_trajectory
from aethernav.baselines.inertial import integrate_planar_inertial
from aethernav.coordinates.enu import wgs84_to_enu
from aethernav.outage.simulator import OutageConfig, simulate_gnss_outage

app = FastAPI(
    title="AetherNav REST API",
    description="Physics-Informed Multi-Modal Intelligent Dead Reckoning API",
    version="0.1.0",
)


class SensorSamplePayload(BaseModel):
    timestamp: float
    sequence_id: Optional[str] = "default"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = 0.0
    speed_mps: Optional[float] = 0.0
    heading_deg: Optional[float] = 0.0
    accelerometer_x: Optional[float] = 0.0
    accelerometer_y: Optional[float] = 0.0
    accelerometer_z: Optional[float] = 9.80665
    gyroscope_x: Optional[float] = 0.0
    gyroscope_y: Optional[float] = 0.0
    gyroscope_z: Optional[float] = 0.0


class EstimateResponse(BaseModel):
    east_m: float
    north_m: float
    heading_deg: float
    speed_mps: float
    confidence: float
    mode: str
    fallback: bool


@app.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "AetherNav",
        "version": "0.1.0",
        "mode": "offline-first-research",
    }


@app.post("/estimate", response_model=EstimateResponse)
def estimate_sample(payload: SensorSamplePayload) -> EstimateResponse:
    confidence = 0.95 if payload.latitude is not None and payload.longitude is not None else 0.50
    mode = "GNSS" if payload.latitude is not None and payload.longitude is not None else "Inertial Dead Reckoning"
    return EstimateResponse(
        east_m=0.0,
        north_m=0.0,
        heading_deg=payload.heading_deg or 0.0,
        speed_mps=payload.speed_mps or 0.0,
        confidence=confidence,
        mode=mode,
        fallback=payload.latitude is None,
    )
