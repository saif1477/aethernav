#!/usr/bin/env python
"""Run Python reference versus ONNX Runtime parity for a validated model."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

parser=argparse.ArgumentParser(); parser.add_argument('--model', default='artifacts/aethernav_integration_test.onnx'); parser.add_argument('--metadata', default='android/AetherNav/app/src/main/assets/aethernav_model_metadata.json'); parser.add_argument('--output', default='artifacts/onnx_parity.json'); args=parser.parse_args()
root=Path(__file__).resolve().parents[1]; model=root/args.model; metadata_path=root/args.metadata; output=root/args.output
result={'status':'not_executed','parity_type':'PYTHON_ONNX_PARITY','python_onnx_parity':False,'android_parity':False,'max_absolute_difference':None,'mean_absolute_difference':None,'max_relative_difference':None,'tolerance':1e-5,'model_hash':None,'metadata_hash':hashlib.sha256(metadata_path.read_bytes()).hexdigest() if metadata_path.exists() else None,'cases':[]}
try:
    import onnxruntime as ort
except ImportError as exc:
    result['reason']=f'Optional parity dependency unavailable: {exc}'
else:
    if not model.exists(): result['reason']=f'Model does not exist: {model}'
    else:
        result['model_hash']=hashlib.sha256(model.read_bytes()).hexdigest()
        meta=json.loads(metadata_path.read_text()); session=ort.InferenceSession(str(model), providers=['CPUExecutionProvider']); input_name=session.get_inputs()[0].name; expected=tuple(meta['input_shape'])
        rng=np.random.default_rng(2026); cases={'zero':np.zeros(expected,np.float32),'seeded_random':rng.normal(size=expected).astype(np.float32),'realistic_normalized':np.array([[[0.2,-0.1,0.0,0.01,0.0,-0.02]]*expected[1]],np.float32),'repeated':rng.normal(size=expected).astype(np.float32)}
        diffs=[]; rels=[]
        for name,x in cases.items():
            ref=x.mean(axis=1); out=session.run(None,{input_name:x})[0]; out2=session.run(None,{input_name:x})[0]; repeat=np.max(np.abs(out-out2)); diff=np.abs(ref-out); diffs.extend(diff.ravel()); rels.extend((diff/np.maximum(np.abs(ref),1e-8)).ravel()); result['cases'].append({'name':name,'shape':list(x.shape),'max_abs':float(diff.max()),'repeat_max_abs':float(repeat),'passed':bool(diff.max()<=result['tolerance'] and repeat==0)})
        try: session.run(None,{input_name:np.zeros((1,1,6),np.float32)}); malformed=False
        except Exception: malformed=True
        result['malformed_shape_rejected']=malformed; result['max_absolute_difference']=float(max(diffs)); result['mean_absolute_difference']=float(np.mean(diffs)); result['max_relative_difference']=float(max(rels)); result['python_onnx_parity']=bool(all(c['passed'] for c in result['cases']) and malformed); result['status']='passed' if result['python_onnx_parity'] else 'failed'
output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2)); raise SystemExit(0 if result['status']=='passed' else 1)
