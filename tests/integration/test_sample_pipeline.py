import subprocess
import sys
from pathlib import Path


def test_sample_pipeline(tmp_path):
    path=tmp_path/'demo.csv'
    subprocess.run([sys.executable,'scripts/create_sample_dataset.py','--output',str(path)],cwd=Path(__file__).parents[2],check=True)
    assert path.exists() and path.stat().st_size > 100
