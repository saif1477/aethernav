#!/usr/bin/env python
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
parser=argparse.ArgumentParser(); parser.add_argument('--model', default='artifacts/aethernav_integration_test.onnx'); parser.add_argument('--metadata', default='android/AetherNav/app/src/main/assets/aethernav_model_metadata.json'); parser.add_argument('--output', default='artifacts/model_manifest.json'); args=parser.parse_args()
root=Path(__file__).resolve().parents[1]; model=root/args.model; metadata=root/args.metadata; data=json.loads(metadata.read_text())
manifest={**{k:data[k] for k in ('model_name','model_version','status','is_trained','input_shape','output_shape','input_dtype','output_dtype','sampling_rate_hz','feature_order','normalization_mean','normalization_std','coordinate_convention','output_units')}, 'accuracy_claims_allowed': bool(data['is_trained']) and data['status']=='trained', 'export_timestamp_utc': datetime.now(timezone.utc).isoformat(), 'source_checkpoint': None, 'dataset_split': None, 'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest() if model.exists() else None, 'metadata_sha256': hashlib.sha256(metadata.read_bytes()).hexdigest(), 'model_path': str(args.model), 'metadata_path': str(args.metadata)}
out=root/args.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(manifest,indent=2))
