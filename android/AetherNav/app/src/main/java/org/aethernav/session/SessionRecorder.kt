package org.aethernav.session

import android.content.Context
import org.aethernav.data.SessionPoint
import java.io.File
import java.util.Locale

class SessionRecorder(private val context: Context) {
    private val points = mutableListOf<SessionPoint>()
    fun append(point: SessionPoint) { points += point }
    fun clear() = points.clear()
    fun snapshot(): List<SessionPoint> = points.toList()
    private fun poseJson(p: org.aethernav.data.LocalPose?) = p?.let { "{\"eastM\":${it.eastM},\"northM\":${it.northM},\"headingDeg\":${it.headingDeg},\"speedMps\":${it.speedMps}}" } ?: "null"

    fun exportJson(): File = File(context.cacheDir, "aethernav-session.json").also { file ->
        file.writeText(points.joinToString(prefix = "[\n", postfix = "\n]") { p ->
            "  {\"timestampSec\":${p.timestampSec},\"aetherNav\":${poseJson(p.pose)},\"reference\":${poseJson(p.reference)},\"baseline\":${poseJson(p.baseline)},\"gnssAvailable\":${p.gnssAvailable},\"outage\":${p.outage},\"mode\":\"${p.mode}\",\"confidence\":${p.confidence},\"fallback\":${p.fallback},\"latencyMs\":${p.latencyMs}}"
        })
    }

    fun exportCsv(): File = File(context.cacheDir, "aethernav-session.csv").also { file ->
        file.printWriter().use { out ->
            out.println("timestamp_sec,aether_east_m,aether_north_m,reference_east_m,reference_north_m,baseline_east_m,baseline_north_m,gnss_available,outage,mode,confidence,fallback,latency_ms")
            points.forEach { p -> out.printf(Locale.US, "%.3f,%.6f,%.6f,%s,%s,%s,%s,%s,%s,%s,%.3f,%s,%d\n", p.timestampSec, p.pose.eastM, p.pose.northM, p.reference?.eastM?.toString() ?: "", p.reference?.northM?.toString() ?: "", p.baseline?.eastM?.toString() ?: "", p.baseline?.northM?.toString() ?: "", p.gnssAvailable, p.outage, p.mode, p.confidence, p.fallback, p.latencyMs) }
        }
    }
}
