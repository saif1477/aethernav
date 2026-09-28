# AetherNav

**Physics-Informed Multi-Modal Intelligent Dead Reckoning for GNSS-Denied Vehicle Navigation**

This repository is an incremental SIH 2026 prototype for SIH26168. The current milestone provides a tested, offline data foundation: a synthetic vehicle sequence, flexible sensor-file loading, data validation, WGS84/local ENU conversion, deterministic sequence splitting, and plotting.

## Quickstart

```bash
cd aethernav
python -m pip install -e '.[dev]'
python scripts/create_sample_dataset.py --output data/sample/demo.csv
python scripts/inspect_dataset.py data/sample/demo.csv
python scripts/plot_sample.py --input data/sample/demo.csv --output artifacts/sample_trajectory.png
pytest -q
```

If installing dependencies is not possible, the runtime itself uses the already available NumPy/pandas/SciPy/Matplotlib stack; pytest is needed for tests.

## Dataset policy

No IO-VNBD data was available locally during Phase 0. Do not commit it. After obtaining it from the official source, use:

```bash
cp /path/to/official/io-vnbd-file.csv data/raw/
python scripts/inspect_dataset.py data/raw/io-vnbd-file.csv
```

The adapter discovers common CSV, JSON, JSONL, and Parquet layouts and reports unsupported/missing fields. Dataset license and attribution must be copied from the official source before publication. See [docs/dataset.md](docs/dataset.md).

## Optional ML and ONNX validation

The base installation does not install large ML runtimes. To install the pinned optional group:

```bash
make install-ml
make validate-onnx
make export
make parity
```

The current integration-test artifact is deterministic and explicitly untrained. It is not valid for navigation accuracy claims.

## Status

See [PROJECT_STATUS.md](PROJECT_STATUS.md), [TODO.md](TODO.md), and [docs/architecture.md](docs/architecture.md). No real-world navigation accuracy is claimed yet.
