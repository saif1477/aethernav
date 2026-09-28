#!/usr/bin/env python
"""Validate the canonical model metadata and an optional ONNX artifact."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.models.contract import ModelContract

parser = argparse.ArgumentParser(); parser.add_argument("--metadata", default="android/AetherNav/app/src/main/assets/aethernav_model_metadata.json"); parser.add_argument("--model", default=None); parser.add_argument("--output", default="artifacts/model_contract_validation.json"); args = parser.parse_args()
root = Path(__file__).resolve().parents[1]; metadata_path = root / args.metadata; data = json.loads(metadata_path.read_text(encoding="utf-8")); required = set(ModelContract().as_dict())
missing = sorted(required - set(data)); errors = []
for key in ("normalization_mean", "normalization_std"):
    if key in data and (len(data[key]) != len(data["feature_order"]) or not np.isfinite(data[key]).all()): errors.append(f"invalid {key}")
if data.get("coordinate_convention") != "local_enu": errors.append("coordinate convention must be local_enu")
if data.get("input_dtype") != "float32" or data.get("output_dtype") != "float32": errors.append("only float32 input/output is supported")
if data.get("input_shape") != [1, data.get("temporal_window_length"), len(data.get("feature_order", []))]: errors.append("input shape does not match temporal window/features")
if len(data.get("output_units", [])) != data.get("output_shape", [0, 0])[-1]: errors.append("output units do not match output shape")
model_status = "not_checked"; model_hash = None
model_path = root / args.model if args.model else None
if model_path:
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest() if model_path.exists() else None
    try:
        import onnx
        model = onnx.load(model_path); inp, out = model.graph.input[0], model.graph.output[0]
        shape = [d.dim_value for d in inp.type.tensor_type.shape.dim]; out_shape = [d.dim_value for d in out.type.tensor_type.shape.dim]
        if shape != data["input_shape"]: errors.append(f"ONNX input shape {shape} != metadata {data['input_shape']}")
        if out_shape != data["output_shape"]: errors.append(f"ONNX output shape {out_shape} != metadata {data['output_shape']}")
        model_status = "checked"
    except ImportError: model_status = "onnx_dependency_unavailable"
    except Exception as exc: errors.append(f"ONNX validation error: {exc}"); model_status = "failed"
result = {"status": "passed" if not missing and not errors else "failed", "missing_fields": missing, "errors": errors, "model_status": model_status, "metadata_hash": hashlib.sha256(metadata_path.read_bytes()).hexdigest(), "model_hash": model_hash, "metadata": data}
out = root / args.output; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); print(json.dumps(result, indent=2)); raise SystemExit(0 if result["status"] == "passed" else 1)
