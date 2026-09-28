import numpy as np
import pytest

from aethernav.metrics.navigation import relative_pose_error, trajectory_metrics, transition_jump


def test_zero_error_metrics():
    ref = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0]], float)
    metrics = trajectory_metrics(ref, ref, [0, 1, 2], reference_velocity=[1, 1, 1], estimate_velocity=[1, 1, 1], reference_heading=[0, 0, 0], estimate_heading=[0, 0, 0])
    assert metrics["ate_rmse_m"] == 0
    assert metrics["endpoint_error_m"] == 0
    assert metrics["velocity_rmse_mps"] == 0
    assert metrics["heading_error_rmse_deg"] == 0
    assert relative_pose_error(ref, ref) == 0


def test_known_error_and_transition():
    ref = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0]], float)
    est = ref.copy(); est[:, 0] += 1
    metrics = trajectory_metrics(ref, est, [0, 1, 2])
    assert metrics["endpoint_error_m"] == pytest.approx(1)
    assert transition_jump(est, 1) == pytest.approx(1)
