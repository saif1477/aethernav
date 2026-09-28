#!/usr/bin/env python
"""Export the validated temporal checkpoint using the canonical model contract."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.models.contract import ModelContract
from aethernav.models.temporal import TemporalDeadReckoner, require_torch

parser = argparse.ArgumentParser(); parser.add_argument("--checkpoint", required=True); parser.add_argument("--output", required=True); args = parser.parse_args()
require_torch()
import torch
contract = ModelContract(); checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False); model = TemporalDeadReckoner(feature_dim=len(contract.feature_order)); model.load_state_dict(checkpoint["model_state"]); model.eval(); example = torch.zeros(contract.input_shape, dtype=torch.float32); output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
torch.onnx.export(model, example, output, input_names=list(contract.input_names), output_names=list(contract.output_names), opset_version=17, dynamo=False)
print(f"exported {output}; validate with: python scripts/validate_model_contract.py --model {output}")
