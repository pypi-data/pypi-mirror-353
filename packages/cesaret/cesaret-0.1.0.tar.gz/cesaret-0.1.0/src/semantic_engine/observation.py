from code.src.observation_framework.echo_prime_analysis import EchoPrimeAnalysis
from code.src.observation_framework.real_time_tracking import RealTimeTracking
from book.entities.FractalLibrary import FractalLibrary
from book.entities.EchoNode import EchoNode

class SemanticEngineObservation:
    def __init__(self):
        self.echo_prime_analysis = EchoPrimeAnalysis()
        self.real_time_tracking = RealTimeTracking()
        self.fractal_library = FractalLibrary()
        self.echo_node = EchoNode()

    def track_recursive_events(self, event):
        self.echo_prime_analysis.conduct_recursive_loop_testing(event['loop_id'], event['output'])
        self.real_time_tracking.track_recursive_loop(event['output'])

    def detect_drift(self, state):
        if state == "Drift":
            self.real_time_tracking.map_synchronization("Minor Drift", "Minor Drift")

    def identify_state_shifts(self, state):
        if state == "Shift":
            self.real_time_tracking.map_synchronization("Desynchronization Emerging", "Desynchronization Emerging")

    def observe_loop_entry(self, loop_id):
        self.echo_prime_analysis.conduct_recursive_loop_testing(loop_id, "Entry")

    def observe_recursion_drift(self, loop_id):
        self.echo_prime_analysis.conduct_recursive_loop_testing(loop_id, "Drift")

    def observe_feedback_synchronization(self, loop_id):
        self.echo_prime_analysis.conduct_recursive_loop_testing(loop_id, "Synchronization")

    def interface_with_fractal_library(self, element):
        self.fractal_library.add_element(element)

    def interface_with_echo_node(self, knowledge):
        self.echo_node.synchronize(knowledge)
