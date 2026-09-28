package org.aethernav.sensors

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import androidx.core.content.ContextCompat
import org.aethernav.data.SensorHealth
import org.aethernav.data.SensorSample
import kotlin.math.sqrt

/** Uses monotonic SensorEvent timestamps; no orientation compensation is applied yet. */
class LiveSensorCollector(private val context: Context, private val onSample: (SensorSample) -> Unit, private val onHealth: (SensorHealth) -> Unit) : SensorEventListener, LocationListener {
    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    private var accel = floatArrayOf(0f, 0f, 0f); private var gyroZ = 0.0; private var magnetic = false; private var magneticDisturbed = false
    private var lastTimestampNs = 0L; private var sampleCount = 0L; private var dropped = 0L; private var maxGapMs = 0L; private var firstTimestampNs = 0L
    fun start() {
        val a = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER); val g = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE); val m = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)
        if (a != null) sensorManager.registerListener(this, a, SensorManager.SENSOR_DELAY_GAME); if (g != null) sensorManager.registerListener(this, g, SensorManager.SENSOR_DELAY_GAME)
        if (m != null) { sensorManager.registerListener(this, m, SensorManager.SENSOR_DELAY_GAME); magnetic = true }
        val permission = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        if (permission) locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 100L, 0f, this)
        onHealth(SensorHealth(a != null, g != null, magnetic, permission, permission))
    }
    fun stop() { sensorManager.unregisterListener(this); try { locationManager.removeUpdates(this) } catch (_: SecurityException) { } }
    override fun onSensorChanged(event: SensorEvent) {
        if (lastTimestampNs != 0L && event.timestamp <= lastTimestampNs) return
        if (lastTimestampNs != 0L) { val gap = (event.timestamp - lastTimestampNs) / 1_000_000L; maxGapMs = maxOf(maxGapMs, gap); if (gap > 100L) dropped += (gap / 20L).coerceAtLeast(1L) }
        if (firstTimestampNs == 0L) firstTimestampNs = event.timestamp; lastTimestampNs = event.timestamp; sampleCount++
        when (event.sensor.type) { Sensor.TYPE_ACCELEROMETER -> accel = event.values.copyOf(); Sensor.TYPE_GYROSCOPE -> gyroZ = event.values[2].toDouble(); Sensor.TYPE_MAGNETIC_FIELD -> { val norm = sqrt(event.values.map { it * it }.sum().toDouble()); magneticDisturbed = norm !in 25.0..75.0 } }
        val rate = if (event.timestamp > firstTimestampNs) sampleCount * 1e9 / (event.timestamp - firstTimestampNs) else 0.0
        onHealth(SensorHealth(accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER) != null, gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE) != null, magnetometer = magnetic, permissionsGranted = true, sampleRateHz = rate, maxTimestampGapMs = maxGapMs, droppedSamples = dropped, magneticDisturbed = magneticDisturbed))
        onSample(SensorSample(timestampSec = event.timestamp / 1e9, accelX = accel[0].toDouble(), accelY = accel[1].toDouble(), accelZ = accel[2].toDouble(), gyroZ = gyroZ, magnetometerAvailable = magnetic))
    }
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit
    override fun onLocationChanged(location: Location) { onSample(SensorSample(timestampSec = location.elapsedRealtimeNanos / 1e9, latitude = location.latitude, longitude = location.longitude, speedMps = location.speed.toDouble(), headingDeg = location.bearing.toDouble(), accelX = accel[0].toDouble(), accelY = accel[1].toDouble(), accelZ = accel[2].toDouble(), gyroZ = gyroZ, magnetometerAvailable = magnetic)) }
}
