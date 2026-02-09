"""
Threat drone movement: erratic but purposeful behaviour.

Biased toward high-value POIs, with loitering, micro-drifts,
heading corrections, and speed modulation. Appears civilian but behaves hostile.
"""

import math
import random
from typing import Tuple, List, Dict, Any

from config.port_botany import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, get_risk_pois
from core.geo import bearing_deg, haversine_km, clamp


def _asset_attraction_vector(
    lat: float, lon: float, pois: List[Dict[str, Any]], strength: float
) -> Tuple[float, float]:
    """
    Compute weighted attraction vector toward high-value POIs.
    Returns (dlat, dlon) in degrees per step.
    """
    total_dlat = 0.0
    total_dlon = 0.0
    total_weight = 0.0

    for poi in pois:
        d_km = haversine_km(lat, lon, poi["lat"], poi["lon"])
        if d_km < 0.01:
            continue
        weight = poi["weight"] / (d_km * d_km + 0.01)
        bearing = bearing_deg(lat, lon, poi["lat"], poi["lon"])
        bearing_rad = math.radians(bearing)
        meters_per_deg_lat = 111_000.0
        meters_per_deg_lon = 111_000.0 * math.cos(math.radians(lat))
        d_north_m = math.cos(bearing_rad) * weight * strength
        d_east_m = math.sin(bearing_rad) * weight * strength
        total_dlat += d_north_m / meters_per_deg_lat
        total_dlon += d_east_m / meters_per_deg_lon
        total_weight += weight

    if total_weight < 0.001:
        return 0.0, 0.0
    scale = min(1.0, strength / total_weight * 0.5)
    return total_dlat * scale / total_weight, total_dlon * scale / total_weight


def step_threat_drone(
    lat: float,
    lon: float,
    heading_deg: float,
    speed_mps: float,
    step: int,
) -> Tuple[float, float, float, float]:
    """
    Advance threat drone position using heading + speed, with:
    - Asset attraction toward POIs
    - Controlled heading noise (micro-drifts)
    - Speed modulation (hover / creep / sprint)

    Returns (new_lat, new_lon, new_heading_deg, new_speed_mps).
    """
    meters_per_deg_lat = 111_000.0
    meters_per_deg_lon = 111_000.0 * math.cos(math.radians(lat))

    # Heading noise: micro-drifts, up to ±30°
    delta_heading = random.uniform(-30.0, 30.0)
    new_heading = (heading_deg + delta_heading) % 360.0

    # Speed modulation: hover, creep, sprint
    r = random.random()
    if r < 0.20:
        new_speed = random.uniform(0.0, 2.0)  # Hover
    elif r < 0.35:
        new_speed = random.uniform(12.0, 18.0)  # Sprint
    else:
        new_speed = max(
            4.0, min(18.0, speed_mps + random.uniform(-0.5, 0.5))
        )  # Creep

    # Base movement from heading + speed
    distance_km = new_speed * 1.0 / 1000.0
    heading_rad = math.radians(new_heading)
    d_north_m = distance_km * 1000.0 * math.cos(heading_rad)
    d_east_m = distance_km * 1000.0 * math.sin(heading_rad)
    dlat = d_north_m / meters_per_deg_lat
    dlon = d_east_m / meters_per_deg_lon if meters_per_deg_lon != 0 else 0.0

    # Asset attraction (bias toward POIs, over land/port)
    pois = get_risk_pois()
    att_dlat, att_dlon = _asset_attraction_vector(lat, lon, pois, 15.0)
    dlat += att_dlat
    dlon += att_dlon

    new_lat = lat + dlat
    new_lon = lon + dlon

    # Bounding box: bounce heading on edge
    bounced = False
    if new_lat < LAT_MIN:
        new_lat = LAT_MIN
        bounced = True
    elif new_lat > LAT_MAX:
        new_lat = LAT_MAX
        bounced = True
    if new_lon < LON_MIN:
        new_lon = LON_MIN
        bounced = True
    elif new_lon > LON_MAX:
        new_lon = LON_MAX
        bounced = True

    if bounced:
        new_heading = (new_heading + 180.0) % 360.0

    new_lat = clamp(new_lat, LAT_MIN, LAT_MAX)
    new_lon = clamp(new_lon, LON_MIN, LON_MAX)

    return new_lat, new_lon, new_heading, new_speed
