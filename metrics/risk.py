"""
Risk zone detection: distance to POIs, weighted risk bubbles.
"""

from typing import Tuple, Dict, Any, Optional, List

from config.port_botany import get_risk_pois
from config.thresholds import RISK_ZONE_RADIUS_KM
from core.geo import haversine_km


def nearest_poi(lat: float, lon: float) -> Tuple[Optional[Dict[str, Any]], float]:
    """Return (poi, distance_km) for the closest high-risk POI."""
    pois = get_risk_pois()
    closest = None
    best_d = float("inf")
    for poi in pois:
        d = haversine_km(lat, lon, poi["lat"], poi["lon"])
        if d < best_d:
            best_d = d
            closest = poi
    return closest, best_d


def is_high_risk_zone(lat: float, lon: float) -> bool:
    """
    Drone is in a high-risk zone when within RISK_ZONE_RADIUS_KM
    of any high-weight POI.
    """
    _, dist_km = nearest_poi(lat, lon)
    return dist_km <= RISK_ZONE_RADIUS_KM


def generate_risk_heat_points() -> List[Dict[str, Any]]:
    """Return POIs as heatmap points for map display."""
    points = []
    for poi in get_risk_pois():
        points.append(
            {
                "lat": poi["lat"],
                "lon": poi["lon"],
                "intensity": poi["weight"],
                "name": poi["name"],
                "category": poi["category"],
            }
        )
    return points
