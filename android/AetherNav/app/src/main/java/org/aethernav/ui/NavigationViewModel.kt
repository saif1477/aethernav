package org.aethernav.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.aethernav.data.*
import org.aethernav.inference.InferenceRepository
import org.aethernav.inference.MockInferenceRepository
import org.aethernav.session.SessionRecorder
import org.aethernav.sensors.LiveSensorCollector
import java.io.File

class NavigationViewModel(app: Application, private val inference: InferenceRepository = MockInferenceRepository()) : AndroidViewModel(app) {
    private val replay = AssetReplayProvider(app)
    private val recorder = SessionRecorder(app)
    private val history = TrajectoryHistory()
    private val _frame = MutableStateFlow<ReplayFrame?>(null); val frame: StateFlow<ReplayFrame?> = _frame.asStateFlow()
    private val _history = MutableStateFlow<List<HistoryPoint>>(emptyList()); val historyPoints: StateFlow<List<HistoryPoint>> = _history.asStateFlow()
    private val _metrics = MutableStateFlow(ReplayMetrics()); val metrics: StateFlow<ReplayMetrics> = _metrics.asStateFlow()
    private val _outage = MutableStateFlow(false); val outage = _outage.asStateFlow()
    private val _running = MutableStateFlow(false); val running = _running.asStateFlow()
    private val _health = MutableStateFlow(SensorHealth()); val health = _health.asStateFlow()
    private val _exported = MutableStateFlow<String?>(null); val exported = _exported.asStateFlow()
    private val _modelStatus = MutableStateFlow("mock-0 • integration-test • imu-v1"); val modelStatus: StateFlow<String> = _modelStatus.asStateFlow()
    private var collector: LiveSensorCollector? = null

    fun toggleOutage() { _outage.value = !_outage.value }
    fun startReplay() { stopLive(); replay.reset(); history.clear(); recorder.clear(); publishHistory(); _running.value = true; stepReplay() }
    fun reset() { _running.value = false; replay.reset(); history.clear(); recorder.clear(); _frame.value = null; publishHistory() }
    fun stepReplay() {
        if (!_running.value) return
        val next = replay.next(_outage.value) ?: run { _running.value = false; return }
        publish(next)
    }
    fun pause() { _running.value = false }
    fun startLive() {
        stopLive(); collector = LiveSensorCollector(getApplication(), { sample ->
            viewModelScope.launch {
                val start = System.nanoTime(); val result = inference.estimate(sample, _frame.value?.aetherNav, null); val latency = (System.nanoTime() - start) / 1_000_000L
                val pose = result.pose; _modelStatus.value = "${result.modelName} ${result.modelVersion} ${if (result.fallback) "fallback" else "active"} ${result.preprocessingVersion}"; val live = ReplayFrame(sample, null, null, pose, pose, result.confidence, result.mode, maxOf(latency, result.latencyMs), gnssAvailable = false, outage = false, fallback = result.fallback)
                publish(live)
            }
        }, { _health.value = it }); collector?.start(); _running.value = true
    }
    fun stopLive() { collector?.stop(); collector = null; _running.value = false }
    fun exportJson(): File { val file = recorder.exportJson(); _exported.value = file.absolutePath; return file }
    fun exportCsv(): File { val file = recorder.exportCsv(); _exported.value = file.absolutePath; return file }
    private fun publish(next: ReplayFrame) { _frame.value = next; val point = HistoryPoint(next.sample.timestampSec, next.reference, next.baseline, next.aetherNav, next.gnssAvailable, next.outage, next.confidence, next.fallback, next.latencyMs); history.add(point); recorder.append(SessionPoint(next.sample.timestampSec, next.aetherNav, next.mode, next.confidence, next.reference, next.baseline, next.gnssAvailable, next.outage, next.fallback, next.latencyMs)); publishHistory() }
    private fun publishHistory() { _history.value = history.snapshot(); _metrics.value = history.metrics() }
    override fun onCleared() { collector?.stop(); super.onCleared() }
}
