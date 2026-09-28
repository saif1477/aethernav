#!/usr/bin/env python
"""Train the optional temporal model on the configured training sequence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.coordinates.enu import wgs84_to_enu
from aethernav.datasets.io_vnbd import load_file
from aethernav.datasets.validation import split_sequences
from aethernav.models.training import make_windows, train_model

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="configs/demo.yaml")
parser.add_argument("--training-config", default="configs/training.yaml")
parser.add_argument("--physics-loss", action="store_true")
parser.add_argument("--magnetometer", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
training = yaml.safe_load((root / args.training_config).read_text(encoding="utf-8"))
frame = load_file(root / config["input"])
splits = split_sequences(frame, config["sequence_split"]["train_fraction"], config["sequence_split"]["validation_fraction"])
sequence = frame[frame.sequence_id.astype(str) == splits["train"][0]].copy()
origin = (float(sequence.latitude.iloc[0]), float(sequence.longitude.iloc[0]), float(sequence.altitude_m.iloc[0]))
reference = wgs84_to_enu(sequence.latitude, sequence.longitude, sequence.altitude_m, origin)
x, y = make_windows(sequence, reference, training["window"], args.magnetometer or training.get("use_magnetometer", False))
try:
    history = train_model(x, y, root / training["checkpoint"], training["epochs"], args.physics_loss or training.get("physics_loss", False), training["seed"], args.magnetometer)
except RuntimeError as exc:
    raise SystemExit(str(exc)) from exc
print(f"trained {len(history)} epochs; checkpoint written to {root / training['checkpoint']}")
