"""
Thresholds for UAV threat metrics and risk classification.
"""

# High-risk zone: drone within this distance (km) of any high-weight POI
RISK_ZONE_RADIUS_KM = 1.0

# Hover detection: distance moved below this (km) counts as hovering
HOVER_DISTANCE_THRESHOLD_KM = 0.01  # ~10 m
