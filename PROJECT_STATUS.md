# AetherNav Project Status

**Date:** 2026-09-24  
**Phase:** 0–4 classical baseline and neural scaffold complete; neural runtime training blocked by unavailable PyTorch  
**Repository state:** New repository; no pre-existing implementation, Git metadata, Android SDK, Gradle, or dataset found in the workspace.

## Environment evidence

- Python: 3.13.14 (meets the Python 3.11+ requirement)
- Available: NumPy, pandas, SciPy, Pydantic, PyYAML, Matplotlib, pytest
- Not installed in the workspace: PyTorch, FastAPI, ONNX Runtime; a PyTorch wheel installation was attempted but failed due temporary filesystem exhaustion
- GPU: not detected/checked because no ML runtime is installed
- Dataset: no IO-VNBD files found under the workspace or shallow filesystem scan
- Git: not initialized
- Android tooling: Gradle/adb not found on PATH

## Working assumptions

1. The first milestone is dependency-light and must run offline with the bundled synthetic sample.
2. IO-VNBD files may have different layouts; the adapter will discover common CSV/JSON/Parquet files and normalize only columns that are actually present.
3. No real-world metric is reported until the dataset is supplied and evaluated.
4. Android and neural inference are intentionally deferred until the Python data contract and replay foundation are tested.

## Evidence from Phase 1–2

Recorded after implementation:

- `python scripts/create_sample_dataset.py --output data/sample/demo.csv` — created 1,800 rows across 3 synthetic sequences at 20 Hz.
- `python scripts/inspect_dataset.py` — 3 sequences, monotonic timestamps within each sequence, no warnings.
- `python scripts/evaluate.py --config configs/demo.yaml` — completed sequence-level split and deterministic outage evaluation.
- `python -m pytest -q` — **12 passed**.
- `ruff check .` — **All checks passed**.
- `python -m compileall -q src scripts tests` — passed.

Generated outputs:

- `artifacts/demo/metrics.json`
- `artifacts/demo/metrics.md`
- `artifacts/demo/splits.json`
- `artifacts/demo/synthetic_2_trajectory.png`
- `artifacts/demo/synthetic_2_error.png`

The reported baseline values are synthetic-provider reference measurements only. They are not IO-VNBD results.

## Phase 3–4 evidence

- `python scripts/evaluate.py --config configs/demo.yaml` — generated GNSS-only, last-velocity, naive-IMU, and EKF plots and metrics.
- `python -m pytest -q` — **12 passed**.
- `ruff check .` — **All checks passed**.
- `python scripts/train.py --config configs/demo.yaml` — correctly stopped with an explicit PyTorch-unavailable message; no fake checkpoint or neural metrics were produced.
- Optional temporal GRU, uncertainty head, physics-informed loss, non-holonomic loss, checkpoint writer, and ablation flags are implemented but require PyTorch to execute.

## Mobile milestone evidence

- Static inspection completed for namespace/application ID, SDK levels, manifest activity/permissions/provider, Compose/Kotlin plugins, assets, lifecycle cleanup, and fallback boundaries.
- Added bounded historical trajectory state with reference/baseline/AetherNav paths and replay metrics.
- Added auto-fit polyline rendering, legend, current-position markers, error/drift/outage/recovery/latency panels, reset behavior, and bounded history tests.
- Added FileProvider `content://` JSON sharing plus cache CSV/JSON export.
- Added live sensor timestamp ordering, gap/dropped-sample estimates, sample-rate diagnostics, magnetic disturbance flag, and explicit no-orientation-compensation documentation.
- Added ONNX Runtime Android dependency, metadata contract, off-main-thread session initialization, input tensor validation path, resource close, and explicit fallback when the model asset is absent or inference fails.
- Added Android CI workflow at `.github/workflows/android.yml`.
- Python regression suite: **12 passed**.
- Android Gradle/device execution was not possible because Gradle, Android SDK, Kotlin compiler, emulator, and device tooling are unavailable in the workspace.

## Explicit validation status

```text
ANDROID_BUILD_STATUS=not_executed
ANDROID_UNIT_TEST_STATUS=not_executed
APK_STATUS=not_generated
ONNX_CONTRACT_STATUS=passed
PYTHON_ONNX_PARITY_STATUS=passed
ANDROID_ONNX_STATUS=not_executed
PHYSICAL_DEVICE_STATUS=not_executed
SHARE_SHEET_STATUS=not_executed
```

Reason for Android/ONNX/device statuses: Gradle, Android SDK, emulator/device, PyTorch, and ONNX Runtime Python packages are not available in the current workspace. No unavailable result has been simulated.

## Validation-gate evidence

- `python -m pytest -q` — **12 passed**.
- `python scripts/generate_model_contract.py` — passed.
- `python scripts/export_integration_test_model.py` — generated the explicitly untrained deterministic integration artifact.
- `python scripts/validate_model_contract.py --model artifacts/aethernav_integration_test.onnx` — passed; ONNX shape and metadata match.
- `python scripts/onnx_parity.py` — **passed** as Python ONNX parity: max absolute difference 0.0, mean absolute difference 0.0, max relative difference 0.0, tolerance 1e-5.
- `python scripts/create_model_manifest.py` — passed; model and metadata hashes recorded.
- Android CI workflow was statically updated with pinned Gradle 8.7, Java 17, Android SDK 35 installation, APK artifact upload, and test-report upload.
- Android build, Android JVM tests, APK generation, Android ONNX execution, emulator, physical-device, share-sheet runtime, and latency remain not executed.

## Risks

- The exact IO-VNBD schema and license must be confirmed from the official distribution before adding dataset-specific assumptions; no IO-VNBD subset was available for this cycle.
- Python 3.13 compatibility of future PyTorch/ONNX packages must be validated in the target environment.
- Android build verification is blocked until an Android SDK/Gradle environment is available.
- The ONNX repository is integrated but intentionally falls back because no validated model asset is bundled; the FastAPI repository remains a development fallback.
