"""WGS84 geodetic and local East-North-Up conversions."""
from __future__ import annotations

import numpy as np

_A = 6378137.0
_E2 = 6.69437999014e-3


def _ecef(lat: np.ndarray, lon: np.ndarray, alt: np.ndarray) -> np.ndarray:
    lat_r, lon_r = np.radians(lat), np.radians(lon)
    n = _A / np.sqrt(1.0 - _E2 * np.sin(lat_r) ** 2)
    return np.stack(((n + alt) * np.cos(lat_r) * np.cos(lon_r),
                     (n + alt) * np.cos(lat_r) * np.sin(lon_r),
                     (n * (1 - _E2) + alt) * np.sin(lat_r)), axis=-1)


def wgs84_to_enu(latitude, longitude, altitude_m=0.0, origin=None) -> np.ndarray:
    lat = np.asarray(latitude, dtype=float); lon = np.asarray(longitude, dtype=float)
    alt = np.broadcast_to(np.asarray(altitude_m, dtype=float), lat.shape)
    if origin is None: origin = (float(lat.flat[0]), float(lon.flat[0]), float(alt.flat[0]))
    ref = _ecef(np.array(origin[0]), np.array(origin[1]), np.array(origin[2]))
    delta = _ecef(lat, lon, alt) - ref
    lat0, lon0 = np.radians(origin[0]), np.radians(origin[1])
    transform = np.array([[-np.sin(lon0), np.cos(lon0), 0],
                          [-np.sin(lat0)*np.cos(lon0), -np.sin(lat0)*np.sin(lon0), np.cos(lat0)],
                          [np.cos(lat0)*np.cos(lon0), np.cos(lat0)*np.sin(lon0), np.sin(lat0)]])
    return delta @ transform.T


def enu_to_wgs84(enu, origin) -> np.ndarray:
    """Inverse conversion, accurate for local trajectories (iterative ECEF inversion)."""
    enu = np.asarray(enu, dtype=float)
    lat0, lon0, alt0 = map(float, origin)
    ref = _ecef(np.array(lat0), np.array(lon0), np.array(alt0))
    lat0r, lon0r = np.radians(lat0), np.radians(lon0)
    transform = np.array([[-np.sin(lon0r), -np.sin(lat0r)*np.cos(lon0r), np.cos(lat0r)*np.cos(lon0r)],
                          [np.cos(lon0r), -np.sin(lat0r)*np.sin(lon0r), np.cos(lat0r)*np.sin(lon0r)],
                          [0, np.cos(lat0r), np.sin(lat0r)]])
    ecef = ref + enu @ transform.T
    x, y, z = ecef[..., 0], ecef[..., 1], ecef[..., 2]
    lon = np.arctan2(y, x); p = np.hypot(x, y); lat = np.arctan2(z, p * (1 - _E2))
    for _ in range(6):
        n = _A / np.sqrt(1 - _E2 * np.sin(lat) ** 2)
        alt = p / np.cos(lat) - n
        lat = np.arctan2(z, p * (1 - _E2 * n / (n + alt)))
    n = _A / np.sqrt(1 - _E2 * np.sin(lat) ** 2)
    alt = p / np.cos(lat) - n
    return np.stack((np.degrees(lat), np.degrees(lon), alt), axis=-1)
