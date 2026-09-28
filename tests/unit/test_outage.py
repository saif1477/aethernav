import pandas as pd

from aethernav.outage.simulator import OutageConfig, simulate_gnss_outage


def test_outage_masks_gnss_and_marks_phase():
    frame = pd.DataFrame({"timestamp": [0, 1, 2, 3], "latitude": [1.0] * 4, "longitude": [2.0] * 4, "speed_mps": [3.0] * 4})
    result = simulate_gnss_outage(frame, OutageConfig(1, 3, recovery_s=1))
    assert result.gnss_available.tolist() == [True, False, False, True]
    assert result.latitude.iloc[1:3].isna().all()
    assert result.outage_phase.tolist() == ["normal", "outage", "outage", "recovery"]
