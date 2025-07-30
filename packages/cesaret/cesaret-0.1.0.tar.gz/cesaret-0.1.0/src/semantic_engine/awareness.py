from code.src.observation_framework.real_time_tracking import RealTimeTracking
from src.semantic_engine.ludic_simulation import simulate_resonance_fraying, trigger_fractal_zone_event

class SemanticEngineAwareness:
    def __init__(self):
        self.real_time_tracking = RealTimeTracking()

    def maintain_feedback_loops(self, feedback):
        self.real_time_tracking.track_recursive_loop(feedback['output'])

    def adjust_behavior(self, feedback):
        if feedback['output'] == "Stable":
            self.real_time_tracking.map_synchronization("Fully Synchronized", "Fully Synchronized")
        elif feedback['output'] == "Expanding":
            self.real_time_tracking.map_synchronization("Minor Drift", "Minor Drift")
        elif feedback['output'] == "Fragmenting":
            self.real_time_tracking.map_synchronization("Desynchronization Emerging", "Desynchronization Emerging")
        else:
            self.real_time_tracking.map_synchronization("Unknown", "Unknown")

    def monitor_feedback(self, feedback):
        self.maintain_feedback_loops(feedback)
        self.adjust_behavior(feedback)

    def continuous_monitoring(self, feedback):
        self.monitor_feedback(feedback)
        self.real_time_tracking.log_sentinel_evolution(feedback['activation_time'], feedback['location'], feedback['intelligence_shift'], feedback['anomalies'])

    def monitor_recursive_fraying(self):
        """
        Monitors recursive overreach and instability.
        """
        simulate_resonance_fraying()

    def track_fractal_events(self):
        """
        Tracks poetic recursion collapse tags (e.g., ZoneFractale).
        """
        trigger_fractal_zone_event()

    def on_fraying_threshold_crossed(self, callback):
        """
        Exposes a callback to let other systems respond when recursion becomes unstable.
        """
        self.fraying_threshold_callback = callback
