# AetherNav mobile demo

1. Open `android/AetherNav` in Android Studio.
2. Build and run the `app` configuration on an Android 26+ emulator or device.
3. Tap **Replay**. Replay uses `app/src/main/assets/sample_replay.csv` and does not require network or permissions.
4. Tap **Next replay sample** to advance deterministically.
5. Toggle **GNSS outage** and continue stepping. The reference, baseline, and AetherNav tracks remain separate.
6. Review error, endpoint, drift, confidence, outage, recovery, and latency panels.
7. Tap **JSON** or **CSV** to write a local session export; tap **Share** to use an Android `content://` FileProvider URI.
8. Tap **Live** only after granting location permission. Sensor availability and timestamp diagnostics are shown in the status panel.

## Validation commands

From the project directory:

```bash
gradle testDebugUnitTest
# or, after generating a wrapper:
./gradlew testDebugUnitTest assembleDebug
```

The current development workspace has no Gradle executable, Android SDK, emulator, or device, so those commands were not executable here.
