package org.aethernav.inference

import android.content.Context
import org.json.JSONObject

data class ModelMetadata(
    val modelName: String,
    val modelVersion: String,
    val status: String,
    val isTrained: Boolean,
    val preprocessingVersion: String,
    val inputShape: List<Long>,
    val featureOrder: List<String>,
    val means: List<Float>,
    val stds: List<Float>,
    val outputShape: List<Long>,
    val outputUnits: List<String>,
    val artifactSha256: String?, 
) {
    companion object {
        fun load(context: Context, assetName: String = "aethernav_model_metadata.json"): ModelMetadata {
            val json = JSONObject(context.assets.open(assetName).bufferedReader().use { it.readText() })
            fun strings(key: String) = buildList { val a = json.getJSONArray(key); repeat(a.length()) { add(a.getString(it)) } }
            fun floats(key: String) = buildList { val a = json.getJSONArray(key); repeat(a.length()) { add(a.getDouble(it).toFloat()) } }
            fun longs(key: String) = buildList { val a = json.getJSONArray(key); repeat(a.length()) { add(a.getLong(it)) } }
            return ModelMetadata(json.getString("model_name"), json.getString("model_version"), json.getString("status"), json.getBoolean("is_trained"), json.getString("preprocessing_version"), longs("input_shape"), strings("feature_order"), floats("normalization_mean"), floats("normalization_std"), longs("output_shape"), strings("output_units"), json.optString("artifact_sha256", null))
        }
    }
}
