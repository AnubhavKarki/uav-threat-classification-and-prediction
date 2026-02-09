"""
JSON export for threat drone telemetry (downstream ML / analysis).
"""

import json

from simulation.drone import Drone


def export_threat_telemetry(drone: Drone, output_path: str) -> None:
    """Export threat drone positions to JSON array."""
    records = []
    for pos in drone.positions:
        record = {
            "timestamp_utc": pos["timestamp"],
            "lat": pos["lat"],
            "lon": pos["lon"],
            "altitude_m": pos["altitude"],
            "drone_id": drone.id,
            "drone_type": drone.role,
            "step": pos["step"],
            "heading_deg": pos["heading_deg"],
            "ground_speed_mps": pos["ground_speed_mps"],
            "in_risk_zone": 1 if pos["in_risk_zone"] else 0,
            "nearest_high_risk": pos["sensor_target"],
            "time_in_risk_zone_s": pos["threat_time_s"],
            "flight_deviation_deg": pos["flight_deviation_deg"],
            "hover_flag": 1 if pos["hovering_duration_s"] > 0.0 else 0,
        }
        records.append(record)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
