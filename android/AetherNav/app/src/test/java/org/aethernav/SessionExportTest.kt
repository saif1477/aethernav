package org.aethernav

import org.aethernav.data.LocalPose
import org.aethernav.data.SessionPoint
import org.junit.Assert.assertTrue
import org.junit.Test

class SessionExportTest {
    @Test fun sessionPointContainsLocalFrameAndConfidence() {
        val point = SessionPoint(1.0, LocalPose(2.0, 3.0, 4.0, 5.0), "Experimental live", 0.5f)
        assertTrue(point.pose.eastM == 2.0 && point.pose.northM == 3.0 && point.confidence == 0.5f)
    }
}
