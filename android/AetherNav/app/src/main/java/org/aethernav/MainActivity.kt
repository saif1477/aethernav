package org.aethernav

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import org.aethernav.data.HistoryPoint
import org.aethernav.data.LocalPose
import org.aethernav.session.shareExport
import org.aethernav.ui.NavigationViewModel

class MainActivity : ComponentActivity() {
    private val permissionLauncher = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        permissionLauncher.launch(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION))
        setContent { AetherNavScreen() }
    }
}

@Composable
fun AetherNavScreen() {
    val context = androidx.compose.ui.platform.LocalContext.current
    val app = context.applicationContext as android.app.Application
    val vm: NavigationViewModel = viewModel(factory = NavigationViewModel.provideFactory(app))
    val frame by vm.frame.collectAsState(); val points by vm.historyPoints.collectAsState(); val modelStatus by vm.modelStatus.collectAsState(); val outage by vm.outage.collectAsState(); val running by vm.running.collectAsState(); val health by vm.health.collectAsState(); val metrics by vm.metrics.collectAsState(); val exported by vm.exported.collectAsState()
    MaterialTheme(colorScheme = darkColorScheme(primary = Color(0xFF00D5FF))) {
        Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("AetherNav", style = MaterialTheme.typography.headlineMedium); Text("EXPERIMENTAL ESTIMATE • local processing", color = Color(0xFFFFC857)); Text("Model: $modelStatus", style = MaterialTheme.typography.bodySmall)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) { Button(onClick = { vm.startReplay() }) { Text("Replay") }; Button(onClick = { vm.startLive() }) { Text("Live") }; Button(onClick = { vm.pause() }) { Text("Pause") }; OutlinedButton(onClick = { vm.reset() }) { Text("Reset") } }
            Row { Text("GNSS outage", modifier = Modifier.weight(1f)); Switch(checked = outage, onCheckedChange = { vm.toggleOutage() }) }
            TrackCanvas(points, frame, Modifier.fillMaxWidth().height(230.dp))
            Legend()
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Metric("Mode", frame?.mode ?: "Idle"); Metric("Confidence", frame?.confidence?.let { "${(it * 100).toInt()}%" } ?: "—"); Metric("Latency", "${frame?.latencyMs ?: 0} ms") }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Metric("Error", metrics.currentErrorM?.let { String.format(java.util.Locale.US, "%.2f m", it) } ?: "—"); Metric("Endpoint", metrics.endpointErrorM?.let { String.format(java.util.Locale.US, "%.2f m", it) } ?: "—"); Metric("Drift/m", metrics.driftPerMeter?.let { String.format(java.util.Locale.US, "%.3f", it) } ?: "—") }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Metric("Speed", frame?.aetherNav?.speedMps?.let { String.format(java.util.Locale.US, "%.1f m/s", it) } ?: "—"); Metric("Heading", frame?.aetherNav?.headingDeg?.let { String.format(java.util.Locale.US, "%.1f°", it) } ?: "—"); Metric("Max error", metrics.maximumErrorM?.let { String.format(java.util.Locale.US, "%.1f m", it) } ?: "—") }
            Text("Outage ${String.format(java.util.Locale.US, "%.1f", metrics.outageDurationSec)}s • Recovery ${String.format(java.util.Locale.US, "%.1f", metrics.recoveryDurationSec)}s • Avg latency ${String.format(java.util.Locale.US, "%.1f", metrics.averageLatencyMs)}ms", style = MaterialTheme.typography.bodySmall)
            Text("Sensors: accel=${health.accelerometer} gyro=${health.gyroscope} mag=${health.magnetometer} GNSS=${health.gnss} rate=${String.format(java.util.Locale.US, "%.1f", health.sampleRateHz)}Hz gaps=${health.maxTimestampGapMs}ms dropped=${health.droppedSamples} magneticDisturbed=${health.magneticDisturbed}", style = MaterialTheme.typography.bodySmall)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) { OutlinedButton(onClick = { vm.exportJson() }) { Text("JSON") }; OutlinedButton(onClick = { vm.exportCsv() }) { Text("CSV") }; OutlinedButton(onClick = { vm.exportJson().also { shareExport(context, it, "application/json") } }) { Text("Share") } }
            exported?.let { Text("Saved locally: $it", style = MaterialTheme.typography.bodySmall) }
            if (running && frame != null) Button(onClick = { vm.stepReplay() }) { Text("Next replay sample") }
        }
    }
}

@Composable private fun Metric(label: String, value: String) { Column { Text(label, style = MaterialTheme.typography.labelSmall); Text(value, style = MaterialTheme.typography.titleMedium) } }
@Composable private fun Legend() { Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { Text("● reference", color = Color.Green); Text("● baseline", color = Color.Red); Text("● AetherNav", color = Color.Cyan) } }

@Composable private fun TrackCanvas(points: List<HistoryPoint>, current: org.aethernav.data.ReplayFrame?, modifier: Modifier) {
    Canvas(modifier) {
        val poses = points.flatMap { listOfNotNull(it.reference, it.baseline, it.aetherNav) }.filter { it.eastM.isFinite() && it.northM.isFinite() }
        if (poses.isEmpty()) return@Canvas
        val minE = poses.minOf { it.eastM }; val maxE = poses.maxOf { it.eastM }; val minN = poses.minOf { it.northM }; val maxN = poses.maxOf { it.northM }; val scale = minOf(size.width / (maxE - minE).coerceAtLeast(1.0).toFloat(), size.height / (maxN - minN).coerceAtLeast(1.0).toFloat()) * .8f
        fun xy(p: LocalPose): Offset? {
            if (!p.eastM.isFinite() || !p.northM.isFinite()) return null
            val x = (p.eastM - minE).toFloat() * scale + size.width * .1f
            val y = size.height - ((p.northM - minN).toFloat() * scale + size.height * .1f)
            if (!x.isFinite() || !y.isFinite()) return null
            return Offset(x, y)
        }
        fun path(selector: (HistoryPoint) -> LocalPose?, color: Color) { points.zipWithNext().forEach { (a, b) -> val p1 = selector(a)?.let { xy(it) }; val p2 = selector(b)?.let { xy(it) }; if (p1 != null && p2 != null) drawLine(color, p1, p2, 4f) } }
        path({ it.reference }, Color.Green); path({ it.baseline }, Color.Red); path({ it.aetherNav }, Color.Cyan)
        current?.reference?.let { xy(it)?.let { o -> drawCircle(Color.Green, 8f, o) } }
        current?.baseline?.let { xy(it)?.let { o -> drawCircle(Color.Red, 7f, o) } }
        current?.aetherNav?.let { xy(it)?.let { o -> drawCircle(Color.Cyan, 7f, o) } }
    }
}
