#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description="Create a clearly labeled synthetic vehicle sequence.")
parser.add_argument("--output", default="data/sample/demo.csv")
parser.add_argument("--duration", type=float, default=30.0)
parser.add_argument("--rate", type=float, default=20.0)
parser.add_argument("--sequences", type=int, default=3)
args = parser.parse_args()
rng = np.random.default_rng(2026)
frames = []
for sequence_index in range(args.sequences):
    t = np.arange(0, args.duration, 1 / args.rate)
    speed = 8.0 + 0.8 * np.sin(t / 4 + sequence_index)
    heading = 12 * np.sin(t / 8 + sequence_index * 0.4) + sequence_index * 8
    distance = np.cumsum(speed / args.rate)
    lat0, lon0 = 13.0827 + sequence_index * 0.01, 80.2707 + sequence_index * 0.01
    lat = lat0 + 0.00001 * distance * np.cos(np.radians(heading))
    lon = lon0 + 0.00001 * distance * np.sin(np.radians(heading)) / np.cos(np.radians(lat0))
    frames.append(pd.DataFrame({"timestamp": t, "sequence_id": f"synthetic_{sequence_index}", "latitude": lat,
        "longitude": lon, "altitude_m": 12.0 + 0.05*np.sin(t), "speed_mps": speed,
        "heading_deg": heading, "accelerometer_x": np.gradient(speed, 1/args.rate),
        "accelerometer_y": 0.01*np.sin(t), "accelerometer_z": 9.80665 + rng.normal(0, 0.01, len(t)),
        "gyroscope_x": 0.0, "gyroscope_y": 0.0,
        "gyroscope_z": np.gradient(np.radians(heading), 1/args.rate)}))
frame = pd.concat(frames, ignore_index=True)
path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True); frame.to_csv(path, index=False)
print(f"created {len(frame)} rows across {args.sequences} synthetic sequences at {path}")
