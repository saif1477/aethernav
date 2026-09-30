package org.aethernav.data

import android.content.Context
import java.io.BufferedReader
import kotlin.math.cos
import kotlin.math.hypot
import kotlin.math.sin

interface ReplayProvider {
    val size: Int
    val index: Int
    fun reset()
    fun next(outageEnabled: Boolean): ReplayFrame?
}

/** Deterministic, offline provider. It never uses wall-clock time or a network. */
class AssetReplayProvider(context: Context, assetName: String = "sample_replay.csv") : ReplayProvider {
    private val samples: List<SensorSample> = try {
        context.assets.open(assetName).bufferedReader().use { reader ->
            reader.lineSequence().drop(1).filter { it.isNotBlank() }.mapNotNull { line ->
                val p = line.split(',').map { it.trim() }
                if (p.size < 7) return@mapNotNull null
                val ts = p[0].toDoubleOrNull() ?: return@mapNotNull null
                val lat = p[1].toDoubleOrNull()
                val lon = p[2].toDoubleOrNull()
                val speed = p[3].toDoubleOrNull() ?: 0.0
                val heading = p[4].toDoubleOrNull() ?: 0.0
                val ax = p[5].toDoubleOrNull() ?: 0.0
                val gz = p[6].toDoubleOrNull() ?: 0.0
                SensorSample(timestampSec = ts, latitude = lat, longitude = lon, speedMps = speed, headingDeg = heading, accelX = ax, gyroZ = gz)
            }.toList()
        }
    } catch (_: Exception) { emptyList() }
    override val size get() = samples.size
    override var index: Int = 0
        private set
    private var lastPose = LocalPose(0.0, 0.0, 0.0, samples.firstOrNull()?.speedMps ?: 0.0)

    override fun reset() { index = 0; lastPose = LocalPose(0.0, 0.0, 0.0, samples.firstOrNull()?.speedMps ?: 0.0) }

    override fun next(outageEnabled: Boolean): ReplayFrame? {
        if (index >= samples.size || samples.isEmpty()) return null
        val sample = samples[index]
        val lat0 = samples.firstOrNull()?.latitude ?: 0.0
        val lon0 = samples.firstOrNull()?.longitude ?: 0.0
        val sampleLat = sample.latitude ?: lat0
        val sampleLon = sample.longitude ?: lon0
        val east = (sampleLon - lon0) * 111320.0 * cos(Math.toRadians(lat0))
        val north = (sampleLat - lat0) * 111132.0
        val reference = LocalPose(east, north, sample.headingDeg ?: 0.0, sample.speedMps ?: 0.0)
        val gnssAvailable = !outageEnabled
        val gnss = if (gnssAvailable) reference else null
        val dt = if (index == 0) 0.0 else sample.timestampSec - samples[index - 1].timestampSec
        val heading = lastPose.headingDeg + Math.toDegrees(sample.gyroZ * dt)
        val speed = lastPose.speedMps + sample.accelX * dt
        val baseline = if (index == 0) lastPose else LocalPose(lastPose.eastM + speed * sin(Math.toRadians(heading)) * dt, lastPose.northM + speed * cos(Math.toRadians(heading)) * dt, heading, speed)
        val aether = if (gnss != null) LocalPose(gnss.eastM, gnss.northM, gnss.headingDeg, gnss.speedMps) else LocalPose(baseline.eastM * 0.98, baseline.northM * 0.98, baseline.headingDeg, baseline.speedMps)
        lastPose = aether
        index++
        return ReplayFrame(sample, reference, gnss, baseline, aether, if (gnss != null) 0.95f else 0.72f, if (gnss != null) "GNSS" else "AetherNav DR", 0L)
    }
}
