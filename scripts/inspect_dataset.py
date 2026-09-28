#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.datasets.io_vnbd import discover_and_load, load_file
from aethernav.datasets.validation import validate_frame

parser = argparse.ArgumentParser(description="Inspect an IO-VNBD-style file or directory.")
parser.add_argument("input", nargs="?", default="data/sample/demo.csv", help="File or directory containing supported tabular data")
args = parser.parse_args()
path = Path(args.input)
if path.is_dir():
    frame, files = discover_and_load(path)
    source = [str(p) for p in files]
else:
    frame = load_file(path)
    source = [str(path)]
report = validate_frame(frame).as_dict()
report["source_files"] = source
print(json.dumps(report, indent=2))
