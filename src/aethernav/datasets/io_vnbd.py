"""Flexible IO-VNBD-style file adapter.

The official distribution is not bundled. This loader accepts common tabular layouts and
keeps unknown source columns, while making no assumptions about unavailable measurements.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from aethernav.schemas import canonicalize_frame


def load_file(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        frame = pd.read_csv(path)
    elif suffix in {".json", ".jsonl"}:
        if suffix == ".jsonl":
            frame = pd.read_json(path, lines=True)
        else:
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            frame = pd.DataFrame(payload)
    elif suffix == ".parquet":
        frame = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported dataset file type: {suffix}")
    return canonicalize_frame(frame)


def discover_and_load(root: str | Path) -> tuple[pd.DataFrame, list[Path]]:
    root = Path(root)
    paths = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".csv", ".txt", ".json", ".jsonl", ".parquet"})
    if not paths:
        raise FileNotFoundError(f"No supported tabular files found under {root}")
    frames = [load_file(path).assign(source_file=str(path)) for path in paths]
    return pd.concat(frames, ignore_index=True, sort=False), paths
