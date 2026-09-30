"""Unit tests for AetherNav API server and canonicalization edge cases."""
from __future__ import annotations

import pandas as pd
import pytest

from aethernav.api.server import app, health_check, estimate_sample, SensorSamplePayload
from aethernav.schemas import canonicalize_frame


def test_api_health_check():
    health = health_check()
    assert health["status"] == "healthy"
    assert health["service"] == "AetherNav"


def test_api_estimate_sample():
    payload = SensorSamplePayload(timestamp=10.0, speed_mps=5.0, heading_deg=45.0)
    response = estimate_sample(payload)
    assert response.confidence == 0.50
    assert response.fallback is True

    gnss_payload = SensorSamplePayload(timestamp=10.0, latitude=13.0827, longitude=80.2707)
    gnss_response = estimate_sample(gnss_payload)
    assert gnss_response.confidence == 0.95
    assert gnss_response.fallback is False


def test_canonicalize_frame_duplicate_columns():
    df = pd.DataFrame({
        "time": [1.0, 2.0],
        "timestamp": [1.0, 2.0],
        "lat": [13.0, 13.1],
        "latitude": [13.0, 13.1],
    })
    canonical = canonicalize_frame(df)
    assert not canonical.columns.duplicated().any()
    assert "timestamp" in canonical.columns
    assert "latitude" in canonical.columns
