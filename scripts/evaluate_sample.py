#!/usr/bin/env python
"""Evaluate geometry of the bundled synthetic reference trajectory.

This is not a navigation-model benchmark. It reports descriptive geometry only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.coordinates.enu import wgs84_to_enu
from aethernav.datasets.io_vnbd import load_file

parser = argparse.ArgumentParser()
parser.add_argument("--input", default="data/sample/demo.csv")
parser.add_argument("--output", default="artifacts/sample_evaluation.json")
args = parser.parse_args()

frame = load_file(args.input)
enu = wgs84_to_enu(
    frame["latitude"].to_numpy(),
    frame["longitude"].to_numpy(),
    frame.get("altitude_m", 0.0).to_numpy(),
)
segment_lengths = np.linalg.norm(np.diff(enu[:, :2], axis=0), axis=1)
result = {
    "provider": "synthetic_sample",
    "reference_only": True,
    "warning": "These are descriptive reference-trajectory values, not model accuracy results.",
    "rows": len(frame),
    "duration_s": float(frame["timestamp"].iloc[-1] - frame["timestamp"].iloc[0]),
    "path_length_m": float(segment_lengths.sum()),
    "endpoint_displacement_m": float(np.linalg.norm(enu[-1, :2] - enu[0, :2])),
    "max_distance_from_origin_m": float(np.linalg.norm(enu[:, :2], axis=1).max()),
}
output = Path(args.output)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
print(f"saved {output}")
