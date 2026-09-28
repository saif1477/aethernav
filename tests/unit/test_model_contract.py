import json
from pathlib import Path

from aethernav.models.contract import ModelContract


def test_canonical_contract_is_self_consistent():
    contract = ModelContract().as_dict()
    assert contract["status"] == "integration-test"
    assert contract["is_trained"] is False
    assert contract["input_shape"] == [1, 20, len(contract["feature_order"])]
    assert contract["output_shape"][-1] == len(contract["output_units"])
    assert len(contract["normalization_mean"]) == len(contract["normalization_std"]) == len(contract["feature_order"])


def test_generated_android_metadata_matches_contract():
    root = Path(__file__).parents[2]
    android = json.loads((root / "android/AetherNav/app/src/main/assets/aethernav_model_metadata.json").read_text())
    expected = ModelContract().as_dict()
    assert all(android[key] == value for key, value in expected.items())
