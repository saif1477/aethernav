# AetherNav Android demo

This is a Kotlin/Jetpack Compose offline-first demo client.

## Modes

- **Replay:** deterministic CSV asset provider; no permissions or network required.
- **Live sensors:** accelerometer, gyroscope, optional magnetometer, and GNSS through Android sensor/location APIs.
- **Inference boundary:** `InferenceRepository` supports mock, future local ONNX, and development FastAPI adapters.

The screen labels estimates as experimental. GNSS outage is a local toggle. Replay retains a bounded historical polyline and calculates error, drift, outage, recovery, and latency metrics. Sessions export to app cache as JSON and CSV; JSON can also be shared through a secure FileProvider `content://` URI.

## Build

Open `android/AetherNav` in Android Studio with an Android SDK and run the `app` configuration. The repository pins Gradle 8.7 in CI, uses Java 17, and installs compileSdk 35. Gradle compilation and unit tests have been verified locally.

## Fallback behavior

- Replay works without permissions, network, GNSS, or sensors.
- Missing magnetometer is reported and does not block operation.
- Permission denial leaves the replay path available.
- ONNX initialization or inference failure falls back explicitly to the deterministic mock repository; the bundled trained model is intentionally absent. The FastAPI adapter remains a development fallback boundary.
- No cloud service is mandatory.
