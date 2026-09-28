package org.aethernav.inference

import android.content.Context
import com.microsoft.onnxruntime.OnnxTensor
import com.microsoft.onnxruntime.OrtEnvironment
import com.microsoft.onnxruntime.OrtSession
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.aethernav.data.LocalPose
import org.aethernav.data.SensorSample
import java.io.Closeable
import java.nio.FloatBuffer
import kotlin.math.exp

 data class InferenceResult(val pose: LocalPose, val confidence: Float, val latencyMs: Long, val mode: String, val fallback: Boolean, val modelVersion: String, val modelName: String = "aethernav_temporal_dead_reckoner", val preprocessingVersion: String = "imu-v1")

interface InferenceRepository { suspend fun estimate(sample: SensorSample, previous: LocalPose?, gnss: LocalPose?): InferenceResult; val name: String }

class MockInferenceRepository : InferenceRepository {
    override val name = "mock"
    override suspend fun estimate(sample: SensorSample, previous: LocalPose?, gnss: LocalPose?): InferenceResult {
        val pose = gnss ?: (previous ?: LocalPose(0.0, 0.0, sample.headingDeg ?: 0.0, sample.speedMps ?: 0.0)).let { it.copy(speedMps = (it.speedMps + sample.accelX * 0.05).coerceAtLeast(0.0)) }
        return InferenceResult(pose, if (gnss != null) .95f else .5f, 0L, if (gnss != null) "GNSS" else "Mock fallback", gnss == null, "mock-0")
    }
}

class DevelopmentApiInferenceRepository : InferenceRepository {
    override val name = "fastapi-development"
    override suspend fun estimate(sample: SensorSample, previous: LocalPose?, gnss: LocalPose?) = MockInferenceRepository().estimate(sample, previous, gnss).copy(mode = "FastAPI fallback")
}

class LocalOnnxInferenceRepository(private val context: Context, private val assetName: String = "aethernav_test.onnx") : InferenceRepository, Closeable {
    override val name = "onnx-local"
    private val window = ArrayDeque<FloatArray>()
    private var metadata: ModelMetadata? = null
    private var environment: OrtEnvironment? = null
    private var session: OrtSession? = null
    private var initError: String? = null
    override suspend fun estimate(sample: SensorSample, previous: LocalPose?, gnss: LocalPose?): InferenceResult = withContext(Dispatchers.Default) {
        val start = System.nanoTime()
        window.addLast(floatArrayOf(sample.accelX.toFloat(), sample.accelY.toFloat(), sample.accelZ.toFloat(), sample.gyroX.toFloat(), sample.gyroY.toFloat(), sample.gyroZ.toFloat()))
        val modelMetadata = runCatching { metadata ?: ModelMetadata.load(context).also { metadata = it } }.getOrElse { return@withContext MockInferenceRepository().estimate(sample, previous, gnss).copy(mode = "ONNX metadata fallback", fallback = true, modelVersion = "none", latencyMs = elapsed(start)) }
        val windowLength = modelMetadata.inputShape.getOrNull(1)?.toInt() ?: return@withContext MockInferenceRepository().estimate(sample, previous, gnss).copy(mode = "ONNX metadata fallback", fallback = true, modelVersion = "none", latencyMs = elapsed(start))
        while (window.size > windowLength) window.removeFirst()
        if (!ensureSession()) return@withContext MockInferenceRepository().estimate(sample, previous, gnss).copy(mode = "ONNX unavailable fallback", fallback = true, modelVersion = "integration-test-0", latencyMs = elapsed(start))
        if (window.size < windowLength) return@withContext MockInferenceRepository().estimate(sample, previous, gnss).copy(mode = "ONNX warm-up fallback", fallback = true, modelVersion = modelMetadata.modelVersion, latencyMs = elapsed(start))
        try {
            val env = environment!!; val active = session!!; val inputName = active.inputNames.first(); val means = modelMetadata.means; val stds = modelMetadata.stds; val values = window.flatMap { it.toList() }.mapIndexed { i, v -> (v - means[i % means.size]) / stds[i % stds.size] }.toFloatArray()
            val tensor = OnnxTensor.createTensor(env, FloatBuffer.wrap(values), modelMetadata.inputShape.toLongArray())
            val result = active.run(mapOf(inputName to tensor)); tensor.close(); result.use {
                val raw = it[0].value; val output = when (raw) { is FloatArray -> raw.toList(); is Array<*> -> raw.flatMap { row -> if (row is FloatArray) row.toList() else emptyList() }; else -> emptyList() }
                val outputWidth = modelMetadata.outputShape.lastOrNull()?.toInt() ?: 0
                if (output.size != outputWidth || outputWidth < 3) throw IllegalArgumentException("ONNX output shape does not match metadata")
                val prior = previous ?: LocalPose(0.0, 0.0, sample.headingDeg ?: 0.0, sample.speedMps ?: 0.0)
                val confidence = exp(-((output[3] + output[4] + output[5]) / 3.0)).toFloat().coerceIn(0f, 1f)
                InferenceResult(LocalPose(prior.eastM + output[0], prior.northM + output[1], prior.headingDeg + Math.toDegrees(output[2].toDouble()), prior.speedMps), confidence, elapsed(start), if (modelMetadata.isTrained) "ONNX trained" else "ONNX integration-test", false, modelMetadata.modelVersion, modelMetadata.modelName, modelMetadata.preprocessingVersion)
            }
        } catch (_: Exception) { MockInferenceRepository().estimate(sample, previous, gnss).copy(mode = "ONNX inference fallback", fallback = true, modelVersion = "integration-test-0", latencyMs = elapsed(start)) }
    }
    private fun elapsed(start: Long) = (System.nanoTime() - start) / 1_000_000L
    private fun ensureSession(): Boolean {
        if (session != null) return true; if (initError != null) return false
        return try { val modelMetadata = metadata ?: ModelMetadata.load(context).also { metadata = it }; if (!ModelIntegrity.verify(context, assetName, modelMetadata.artifactSha256)) throw SecurityException("model hash mismatch or missing hash"); val env = OrtEnvironment.getEnvironment(); val bytes = context.assets.open(assetName).use { it.readBytes() }; environment = env; session = env.createSession(bytes, OrtSession.SessionOptions()); true } catch (e: Exception) { initError = e.message ?: "model load failed"; false }
    }
    fun reset() { window.clear() }
    override fun close() { session?.close(); session = null; environment = null; window.clear() }
}
