#!/usr/bin/env python
"""Create a deterministic, explicitly untrained ONNX integration-test model."""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sys
import onnx
from onnx import TensorProto, helper
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.models.contract import ModelContract

root = Path(__file__).resolve().parents[1]; out = root / "artifacts/aethernav_integration_test.onnx"
contract = ModelContract()
input_info = helper.make_tensor_value_info(contract.input_names[0], TensorProto.FLOAT, contract.input_shape)
output_info = helper.make_tensor_value_info(contract.output_names[0], TensorProto.FLOAT, contract.output_shape)
node = helper.make_node("ReduceMean", [contract.input_names[0]], [contract.output_names[0]], axes=[1], keepdims=0)
graph = helper.make_graph([node], "aethernav_integration_test", [input_info], [output_info])
model = helper.make_model(graph, producer_name="aethernav", opset_imports=[helper.make_opsetid("", 13)])
model.ir_version = 9
onnx.checker.check_model(model); out.parent.mkdir(parents=True, exist_ok=True); onnx.save(model, out)
android_asset = root / "android/AetherNav/app/src/main/assets/aethernav_test.onnx"; android_asset.write_bytes(out.read_bytes())
metadata_path = root / "android/AetherNav/app/src/main/assets/aethernav_model_metadata.json"; metadata = json.loads(metadata_path.read_text(encoding="utf-8")); metadata["artifact_file"] = "aethernav_test.onnx"; metadata["artifact_sha256"] = hashlib.sha256(android_asset.read_bytes()).hexdigest(); metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print(f"created {out}"); print(f"copied {android_asset}"); print(f"updated {metadata_path}")
