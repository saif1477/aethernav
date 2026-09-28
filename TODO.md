# AetherNav Task Plan

## Phase 0 — repository inspection

- [x] Inspect repository, Python, tooling, Git state, and dataset availability
- [x] Record assumptions and risks
- [x] Create initial architecture document

## Phase 1 — data and coordinate pipeline

- [x] Define canonical sample schema
- [x] Implement robust CSV/JSON/JSONL/Parquet adapter with column alias discovery
- [x] Implement WGS84 to local ENU and inverse conversion
- [x] Implement validation report for timestamps, gaps, NaNs, outliers, and coordinates
- [x] Implement deterministic sequence-level splitting metadata
- [x] Generate bundled multi-sequence synthetic provider for offline CI/demo
- [x] Add unit tests and a trajectory plot command
- [ ] Validate against an official IO-VNBD download when provided

## Phase 2 — outages, baseline, and metrics

- [x] Implement deterministic GNSS outage masking and recovery flags
- [x] Implement transparent planar naive inertial integration baseline
- [x] Implement ATE, RPE, endpoint, drift, velocity, heading, threshold, and transition metrics
- [x] Generate trajectory PNG, error PNG, JSON metrics, Markdown report, and split metadata
- [x] Add outage, metrics, and end-to-end evaluation tests

## Phase 3–4 — baselines and temporal model

- [x] GNSS-only baseline
- [x] Last-velocity baseline
- [x] Naive planar IMU integration
- [x] Planar EKF baseline
- [x] Local-ENU temporal GRU with motion-increment outputs and uncertainty head
- [x] Physics-informed and non-holonomic loss functions
- [x] Checkpointing and training CLI with physics/magnetometer ablation flags
- [x] Comparative synthetic baseline plots and metrics
- [ ] Execute neural training after installing a compatible PyTorch wheel
- [ ] Execute on an official IO-VNBD subset when supplied

## Mobile milestones 1–3

- [x] Define canonical Python-generated model contract
- [x] Generate Android metadata from Python contract
- [x] Add contract validation and explicit no-model parity status
- [x] Add Android model-status panel
- [x] Add Android CI caching, build/test steps, APK and test-report artifacts

- [x] Static Android project inspection and CI workflow
- [x] Bounded historical replay history and reset behavior
- [x] Reference, baseline, and AetherNav historical polylines with legend/current markers
- [x] Live error, endpoint, max/mean error, drift, confidence, outage/recovery, and latency metrics
- [x] Sensor timestamp ordering, gap/dropped-sample diagnostics, and magnetic disturbance flag
- [x] FileProvider JSON share sheet plus CSV/JSON cache export
- [x] ONNX Runtime Android repository boundary, metadata, background initialization, and fallback handling
- [x] Android JVM tests for history, replay state, outage transitions, and session state
- [x] Pin CI Gradle 8.7 and configure Android SDK 35/test/APK artifact steps
- [x] Generate deterministic integration-test ONNX artifact with explicit non-trained status
- [x] Run Python ONNX parity and record hashes
- [ ] Run Gradle unit tests and debug build on an Android-enabled runner
- [ ] Run Android ONNX parity on an emulator/device
- [ ] Bundle a validated trained ONNX model and run device parity/latency tests

## Next three tasks

1. Run the Android CI workflow or local Gradle build on an Android-enabled environment.
2. Bundle a validated trained ONNX model and run device parity/latency tests.
3. Validate live sensor orientation and timestamp behavior on physical hardware.
