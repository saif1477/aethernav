# Validation matrix and metrics status

| Capability | Static | CI | APK | Emulator | Physical device | Measured |
|------------|--------|-----|-----|----------|-----------------|----------|
| Python tests | pass | not_executed | not_applicable | not_applicable | not_applicable | 12 passed |
| Android compile | pass | not_executed | not_generated | not_executed | not_executed | no local Gradle/SDK |
| Android JVM tests | pass (source) | not_executed | not_generated | not_executed | not_applicable | not executed |
| Replay mode | pass (source/assets) | not_executed | not_generated | not_executed | not_executed | not measured |
| Historical paths | pass (source) | not_executed | not_generated | not_executed | not_executed | not measured |
| Share sheet | pass (XML/source) | not_executed | not_generated | not_executed | not_executed | not measured |
| ONNX initialization | pass (source/contract) | not_executed | not_generated | not_executed | not_executed | not measured |
| ONNX inference | pass (source) | not_executed | not_generated | not_executed | not_executed | not measured |
| Python ONNX parity | pass | not_executed | not_applicable | not_applicable | not_applicable | max/mean abs diff 0.0 |
| Sensor collection | pass (source) | not_executed | not_generated | not_executed | not_executed | not measured |
| Navigation accuracy | not_applicable | not_applicable | not_generated | not_executed | not_executed | no claim |

## Model artifact

The available artifact is a deterministic integration-test ONNX model:

- Model: `artifacts/aethernav_integration_test.onnx`
- Status: `integration-test`
- Trained: `false`
- Accuracy claims allowed: `false`
- Input: `[1, 20, 6]`, float32
- Output: `[1, 6]`, float32
- Model SHA-256: `0a1fa6139bbda8824321fe0cc254915d90e32339c2675e79739bedc6fdb717ea`
- Metadata SHA-256: `e3236a21bf25adb0bed36f63fb1b3e9d43b17bb573221a7f322bb9e6a4c2b079`

## Python parity

`python scripts/onnx_parity.py` passed for zero, seeded-random, realistic normalized, repeated deterministic, and malformed-shape cases.

- Maximum absolute difference: `0.0`
- Mean absolute difference: `0.0`
- Maximum relative difference: `0.0`
- Tolerance: `1e-5`

This is **Python ONNX parity**, not Android parity or physical-device parity.
