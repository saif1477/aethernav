"""Dataset validation and sequence-level splitting."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from aethernav.schemas import DatasetReport


def validate_frame(frame: pd.DataFrame) -> DatasetReport:
    ts = pd.to_numeric(frame["timestamp"], errors="coerce")
    sequence = frame.get("sequence_id", pd.Series("default", index=frame.index)).astype(str)
    diffs = frame.assign(_timestamp=ts, _sequence=sequence).groupby("_sequence")["_timestamp"].diff().dropna()
    warnings: list[str] = []
    if ts.isna().any(): warnings.append("timestamp contains NaN/non-numeric values")
    if len(diffs) and (diffs <= 0).any(): warnings.append("timestamps are not strictly increasing within a sequence")
    if len(diffs) and (diffs > 10 * diffs[diffs > 0].median()).any(): warnings.append("large timestamp gap detected")
    numeric = frame.select_dtypes(include=[np.number])
    if numeric.size and np.isinf(numeric.to_numpy()).any(): warnings.append("infinite numeric value detected")
    bounds = None
    if {"latitude", "longitude"}.issubset(frame):
        bounds = {f"{c}_{side}": float(getattr(frame[c], side)()) for c in ("latitude", "longitude") for side in ("min", "max")}
        if ((frame.latitude.abs() > 90) | (frame.longitude.abs() > 180)).any(): warnings.append("invalid geographic coordinate")
    rate = float(1.0 / diffs[diffs > 0].median()) if (diffs > 0).any() else None
    duplicate_timestamps = int(frame.assign(_timestamp=ts, _sequence=sequence).duplicated(["_sequence", "_timestamp"]).sum())
    return DatasetReport(len(frame), list(frame.columns), int(sequence.nunique()), bool((diffs > 0).all()), duplicate_timestamps, {k: int(v) for k, v in frame.isna().sum().items() if v}, rate, bounds, warnings)


def split_sequences(frame: pd.DataFrame, train=0.7, validation=0.15) -> dict[str, list[str]]:
    ids = sorted(frame.get("sequence_id", pd.Series(["default"])).astype(str).unique())
    n_train = max(1, int(len(ids) * train)) if ids else 0
    n_val = max(1, int(len(ids) * validation)) if len(ids) >= 3 else 0
    if n_train + n_val >= len(ids) and len(ids) > 1:
        n_train = max(1, len(ids) - n_val - 1)
    return {"train": ids[:n_train], "validation": ids[n_train:n_train+n_val], "test": ids[n_train+n_val:]}


def save_split_metadata(splits: dict[str, list[str]], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(splits, indent=2), encoding="utf-8")
