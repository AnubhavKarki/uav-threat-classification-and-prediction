"""
Behaviour metrics: hover duration, heading change, speed, sensor orientation.
"""

from config.constants import SECONDS_PER_STEP
from config.thresholds import HOVER_DISTANCE_THRESHOLD_KM
from core.geo import haversine_km, bearing_deg
from metrics.risk import nearest_poi, is_high_risk_zone


def enrich_positions_with_metrics(drones: list) -> None:
    """
    Compute per-step metrics and attach to each position.
    Modifies drone.positions in place.
    """
    for drone in drones:
        threat_time_s = 0.0
        hover_streak = 0.0
        last_lat = None
        last_lon = None
        last_heading = None

        enriched = []
        for pos in drone.positions:
            lat = pos["lat"]
            lon = pos["lon"]
            altitude = pos["altitude"]
            ts_str = pos["timestamp"]
            step = pos["step"]

            in_risk = is_high_risk_zone(lat, lon)

            distance_km = 0.0
            heading_deg_val = None
            flight_deviation_deg = 0.0

            if last_lat is not None and last_lon is not None:
                distance_km = haversine_km(last_lat, last_lon, lat, lon)
                if distance_km > 0.0:
                    heading_deg_val = bearing_deg(last_lat, last_lon, lat, lon)

            if distance_km < HOVER_DISTANCE_THRESHOLD_KM:
                hover_streak += SECONDS_PER_STEP
            else:
                hover_streak = 0.0

            if in_risk:
                threat_time_s += SECONDS_PER_STEP

            if heading_deg_val is not None and last_heading is not None:
                diff = abs(heading_deg_val - last_heading)
                if diff > 180.0:
                    diff = 360.0 - diff
                flight_deviation_deg = diff

            poi, _ = nearest_poi(lat, lon)
            if poi:
                sensor_orientation_deg = bearing_deg(lat, lon, poi["lat"], poi["lon"])
                sensor_target = poi["name"]
            else:
                sensor_orientation_deg = None
                sensor_target = None

            enriched.append(
                {
                    "lat": lat,
                    "lon": lon,
                    "altitude": altitude,
                    "timestamp": ts_str,
                    "step": step,
                    "in_risk_zone": in_risk,
                    "distance_km": distance_km,
                    "hovering_duration_s": hover_streak,
                    "flight_deviation_deg": flight_deviation_deg,
                    "sensor_orientation_deg": sensor_orientation_deg,
                    "sensor_target": sensor_target,
                    "heading_deg": heading_deg_val,
                    "ground_speed_mps": distance_km * 1000.0 / SECONDS_PER_STEP,
                    "threat_time_s": threat_time_s,
                }
            )

            last_lat, last_lon = lat, lon
            if heading_deg_val is not None:
                last_heading = heading_deg_val

        drone.positions = enriched
