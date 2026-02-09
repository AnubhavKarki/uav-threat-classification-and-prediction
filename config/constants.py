"""
Simulation constants for UAV Threat Classification.

Centralizes numerical parameters used across the simulation.
"""

NUM_DRONES = 5
NUM_STEPS = 80  # More steps for smoother animation

ALTITUDE_MIN = 30.0
ALTITUDE_MAX = 150.0

# Log and output file paths
LOG_FILE = "drone_log.txt"
MAP_FILE = "drone_locations.html"
METRICS_LOG_FILE = "drone_metrics.txt"
THREAT_JSON_FILE = "threat_telemetry.json"

# Simulation timing
SECONDS_PER_STEP = 1.0
