package org.aethernav

import org.aethernav.data.ReplayStateMachine
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ReplayStateMachineTest {
    @Test fun replayStartsPausedThenRuns() { val state = ReplayStateMachine(); assertFalse(state.state.running); state.startReplay(); assertTrue(state.state.running); assertEquals("Replay", state.state.mode) }
    @Test fun outageTransitionIsDeterministic() { val state = ReplayStateMachine(); state.startReplay(); state.toggleOutage(); assertTrue(state.state.outage); state.toggleOutage(); assertFalse(state.state.outage) }
    @Test fun resetClearsSessionState() { val state = ReplayStateMachine(); state.startReplay(); state.toggleOutage(); state.reset(); assertEquals("Idle", state.state.mode); assertFalse(state.state.running); assertFalse(state.state.outage) }
}
