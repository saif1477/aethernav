"""Reproducible trajectory and transition metrics."""
from __future__ import annotations

import numpy as np


def _finite_rows(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    mask = np.isfinite(a).all(axis=1) & np.isfinite(b).all(axis=1)
    return a[mask], b[mask], mask


def trajectory_metrics(reference_enu, estimate_enu, timestamps=None, reference_velocity=None,
                       estimate_velocity=None, reference_heading=None, estimate_heading=None,
                       outage_mask=None, thresholds=(1.0, 5.0, 10.0)) -> dict[str, float | int | None]:
    ref, est, valid = _finite_rows(reference_enu, estimate_enu)
    if not len(ref):
        raise ValueError("no finite trajectory pairs available")
    errors = np.linalg.norm(est[:, :2] - ref[:, :2], axis=1)
    result: dict[str, float | int | None] = {
        "sample_count": len(errors), "ate_rmse_m": float(np.sqrt(np.mean(errors ** 2))),
        "horizontal_position_error_mean_m": float(np.mean(errors)),
        "horizontal_position_error_median_m": float(np.median(errors)),
        "horizontal_position_error_p95_m": float(np.percentile(errors, 95)),
        "endpoint_error_m": float(errors[-1]),
        "max_error_m": float(np.max(errors)),
    }
    if timestamps is not None:
        dt = float(np.asarray(timestamps)[-1] - np.asarray(timestamps)[0])
        distance = float(np.sum(np.linalg.norm(np.diff(ref[:, :2], axis=0), axis=1))) if len(ref) > 1 else 0.0
        result["drift_per_meter"] = float(result["endpoint_error_m"] / distance) if distance > 0 else None
        result["drift_per_second_m"] = float(result["endpoint_error_m"] / dt) if dt > 0 else None
    else:
        result["drift_per_meter"] = None; result["drift_per_second_m"] = None
    for threshold in thresholds:
        result[f"within_{threshold:g}m_fraction"] = float(np.mean(errors <= threshold))
    if reference_velocity is not None and estimate_velocity is not None:
        rv, ev, _ = _finite_rows(np.asarray(reference_velocity).reshape(-1, 1), np.asarray(estimate_velocity).reshape(-1, 1))
        result["velocity_rmse_mps"] = float(np.sqrt(np.mean((rv[:, 0] - ev[:, 0]) ** 2)))
    else:
        result["velocity_rmse_mps"] = None
    if reference_heading is not None and estimate_heading is not None:
        rh, eh = np.asarray(reference_heading, float), np.asarray(estimate_heading, float)
        delta = (eh - rh + 180.0) % 360.0 - 180.0
        result["heading_error_mean_deg"] = float(np.mean(np.abs(delta)))
        result["heading_error_rmse_deg"] = float(np.sqrt(np.mean(delta ** 2)))
    else:
        result["heading_error_mean_deg"] = None; result["heading_error_rmse_deg"] = None
    if outage_mask is not None:
        mask = np.asarray(outage_mask, bool)[valid]
        result["outage_samples"] = int(mask.sum())
        result["outage_ate_rmse_m"] = float(np.sqrt(np.mean(errors[mask] ** 2))) if mask.any() else None
    else:
        result["outage_samples"] = None; result["outage_ate_rmse_m"] = None
    return result


def transition_jump(trajectory, transition_index: int) -> float:
    trajectory = np.asarray(trajectory, float)
    if transition_index <= 0 or transition_index >= len(trajectory):
        raise ValueError("transition index must be inside trajectory")
    return float(np.linalg.norm(trajectory[transition_index, :2] - trajectory[transition_index - 1, :2]))


def relative_pose_error(reference_enu, estimate_enu, delta: int = 1) -> float:
    ref, est = np.asarray(reference_enu, float), np.asarray(estimate_enu, float)
    if delta <= 0 or len(ref) <= delta:
        raise ValueError("delta must be positive and smaller than trajectory length")
    ref_rel = ref[delta:] - ref[:-delta]
    est_rel = est[delta:] - est[:-delta]
    return float(np.sqrt(np.mean(np.sum((est_rel[:, :2] - ref_rel[:, :2]) ** 2, axis=1))))
