package org.aethernav.data

data class SensorSample(
    val timestampSec: Double,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val speedMps: Double? = null,
    val headingDeg: Double? = null,
    val accelX: Double = 0.0,
    val accelY: Double = 0.0,
    val accelZ: Double = 9.80665,
    val gyroX: Double = 0.0,
    val gyroY: Double = 0.0,
    val gyroZ: Double = 0.0,
    val magnetometerAvailable: Boolean = false,
)

data class LocalPose(val eastM: Double, val northM: Double, val headingDeg: Double, val speedMps: Double)
data class ReplayFrame(
    val sample: SensorSample,
    val reference: LocalPose?,
    val gnss: LocalPose?,
    val baseline: LocalPose,
    val aetherNav: LocalPose,
    val confidence: Float,
    val mode: String,
    val latencyMs: Long,
    val gnssAvailable: Boolean = gnss != null,
    val outage: Boolean = gnss == null,
    val fallback: Boolean = false,
    val errorM: Double? = reference?.let { kotlin.math.hypot(it.eastM - aetherNav.eastM, it.northM - aetherNav.northM) },
)

data class SensorHealth(
    val accelerometer: Boolean = false,
    val gyroscope: Boolean = false,
    val magnetometer: Boolean = false,
    val gnss: Boolean = false,
    val permissionsGranted: Boolean = false,
    val sampleRateHz: Double = 0.0,
    val maxTimestampGapMs: Long = 0L,
    val droppedSamples: Long = 0L,
    val magneticDisturbed: Boolean = false,
)
data class SessionPoint(
    val timestampSec: Double,
    val pose: LocalPose,
    val mode: String,
    val confidence: Float,
    val reference: LocalPose? = null,
    val baseline: LocalPose? = null,
    val gnssAvailable: Boolean = false,
    val outage: Boolean = false,
    val fallback: Boolean = false,
    val latencyMs: Long = 0L,
)
