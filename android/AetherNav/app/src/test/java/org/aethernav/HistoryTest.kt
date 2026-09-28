package org.aethernav

import org.aethernav.data.HistoryPoint
import org.aethernav.data.LocalPose
import org.aethernav.data.TrajectoryHistory
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test

class HistoryTest {
    private fun point(t: Double, ref: LocalPose? = LocalPose(t, 0.0, 0.0, 1.0)) = HistoryPoint(t, ref, LocalPose(t, 0.0, 0.0, 1.0), LocalPose(t + 1.0, 0.0, 0.0, 1.0), true, false, .8f, false, 2)
    @Test fun emptyHistoryHasNoError() { assertNull(TrajectoryHistory().metrics().currentErrorM) }
    @Test fun historyIsBoundedAndResettable() { val h = TrajectoryHistory(2); h.add(point(0.0)); h.add(point(1.0)); h.add(point(2.0)); assertEquals(2, h.snapshot().size); h.clear(); assertEquals(0, h.snapshot().size) }
    @Test fun errorAndDriftAreComputed() { val h = TrajectoryHistory(); h.add(point(0.0)); h.add(point(1.0)); assertNotNull(h.metrics().currentErrorM); assertNotNull(h.metrics().driftPerMeter) }
    @Test fun missingReferenceDoesNotCreateError() { val h = TrajectoryHistory(); h.add(point(0.0, null)); assertNull(h.metrics().currentErrorM) }
}
