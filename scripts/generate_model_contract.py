#!/usr/bin/env python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.models.contract import write_contract

root = Path(__file__).resolve().parents[1]
print(write_contract(root / "android/AetherNav/app/src/main/assets/aethernav_model_metadata.json"))
print(write_contract(root / "artifacts/model_contract.json"))
