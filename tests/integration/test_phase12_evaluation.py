import json
import subprocess
import sys
from pathlib import Path


def test_phase12_evaluation(tmp_path):
    root = Path(__file__).parents[2]
    sample = tmp_path / "sample.csv"
    out = tmp_path / "out"
    subprocess.run([sys.executable, "scripts/create_sample_dataset.py", "--output", str(sample)], cwd=root, check=True)
    config = tmp_path / "demo.yaml"
    config.write_text(f"input: {sample}\noutput_dir: {out}\nseed: 2026\noutage:\n  start_s: 10\n  end_s: 20\n  recovery_s: 2\n  noise_std_m: 0\nsequence_split:\n  train_fraction: 0.6\n  validation_fraction: 0.2\n")
    subprocess.run([sys.executable, "scripts/evaluate.py", "--config", str(config)], cwd=root, check=True)
    report = json.loads((out / "metrics.json").read_text())
    assert report["split"]["test"] and (out / "metrics.md").exists()
