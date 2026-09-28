package org.aethernav.data

import kotlin.math.sqrt

data class HistoryPoint(
    val timestampSec: Double,
    val reference: LocalPose?,
    val baseline: LocalPose,
    val aetherNav: LocalPose,
    val gnssAvailable: Boolean,
    val outage: Boolean,
    val confidence: Float,
    val fallback: Boolean,
    val latencyMs: Long,
)

data class ReplayMetrics(
    val currentErrorM: Double? = null,
    val endpointErrorM: Double? = null,
    val maximumErrorM: Double? = null,
    val meanErrorM: Double? = null,
    val driftPerMeter: Double? = null,
    val outageDurationSec: Double = 0.0,
    val recoveryDurationSec: Double = 0.0,
    val averageLatencyMs: Double = 0.0,
    val maximumLatencyMs: Long = 0L,
)

class TrajectoryHistory(private val maxPoints: Int = 10_000) {
    private val values = ArrayDeque<HistoryPoint>()
    fun add(point: HistoryPoint) { values.addLast(point); while (values.size > maxPoints) values.removeFirst() }
    fun clear() = values.clear()
    fun snapshot(): List<HistoryPoint> = values.toList()
    fun metrics(): ReplayMetrics {
        val points = values.toList(); val errors = points.mapNotNull { p -> p.reference?.let { sqrt((it.eastM - p.aetherNav.eastM) * (it.eastM - p.aetherNav.eastM) + (it.northM - p.aetherNav.northM) * (it.northM - p.aetherNav.northM)) } }
        val traveled = points.zipWithNext().sumOf { (a, b) -> sqrt((b.aetherNav.eastM - a.aetherNav.eastM) * (b.aetherNav.eastM - a.aetherNav.eastM) + (b.aetherNav.northM - a.aetherNav.northM) * (b.aetherNav.northM - a.aetherNav.northM)) }
        val outageTimes = points.filter { it.outage }.map { it.timestampSec }; val recoveryStart = points.indexOfFirst { it.outage }.takeIf { it >= 0 }?.let { i -> points.drop(i).firstOrNull { !it.outage }?.timestampSec }
        val outageStart = outageTimes.firstOrNull(); val recoveryDuration = if (outageStart != null && recoveryStart != null) recoveryStart - outageStart else 0.0
        return ReplayMetrics(errors.lastOrNull(), errors.lastOrNull(), errors.maxOrNull(), errors.averageOrNull(), errors.lastOrNull()?.let { if (traveled > 0) it / traveled else null }, (outageTimes.lastOrNull() ?: 0.0) - (outageStart ?: 0.0), recoveryDuration, points.map { it.latencyMs.toDouble() }.averageOrNull() ?: 0.0, points.maxOfOrNull { it.latencyMs } ?: 0L)
    }
    private fun List<Double>.averageOrNull() = if (isEmpty()) null else average()
}
