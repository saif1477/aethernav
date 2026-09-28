package org.aethernav.data

data class SessionState(val running: Boolean = false, val outage: Boolean = false, val mode: String = "Idle")

class ReplayStateMachine {
    var state = SessionState(); private set
    fun startReplay() { state = SessionState(true, state.outage, "Replay") }
    fun pause() { state = state.copy(running = false) }
    fun toggleOutage() { state = state.copy(outage = !state.outage) }
    fun reset() { state = SessionState() }
}
