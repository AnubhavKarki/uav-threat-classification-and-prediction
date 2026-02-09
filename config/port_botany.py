"""
Port Botany high-value locations for UAV threat assessment.

Authoritative POIs driving risk heatmap intensity, sensor targeting,
and threat scoring. Based on real-world coordinates near Port Botany, Australia.
"""

from typing import List, Dict, Any

# Approximate centre of Port Botany container terminal
PORT_BOTANY_CENTER_LAT = -33.9760
PORT_BOTANY_CENTER_LON = 151.2180

# Tight bounding box: drones stay over terminal and harbour approaches
LAT_MIN, LAT_MAX = -33.992, -33.958
LON_MIN, LON_MAX = 151.205, 151.230

# Broader city bounding box for risk grid (legacy compatibility)
CITY_LAT_MIN, CITY_LAT_MAX = -34.05, -33.82
CITY_LON_MIN, CITY_LON_MAX = 151.05, 151.30

# Representative assets (ships / cranes) within Port Botany
SHIP_1 = (-33.9720, 151.2120)  # Central ship
SHIP_2 = (-33.9740, 151.2180)  # Ship for threat drone orbit
CRANE_1 = (-33.9695, 151.2085)
CRANE_2 = (-33.9685, 151.2200)


def get_risk_pois() -> List[Dict[str, Any]]:
    """
    Authoritative high-value locations near Port Botany.

    Each POI includes:
      - name: Human-readable label
      - lat, lon: Coordinates
      - weight: Risk intensity (0–1)
      - category: "port" | "naval" | "harbour"
    """
    return [
        {
            "name": "Port Botany Main Container Terminal",
            "lat": -33.9754,
            "lon": 151.2218,
            "weight": 1.0,
            "category": "port",
        },
        {
            "name": "Bulk Liquids Berths",
            "lat": -33.9775,
            "lon": 151.2155,
            "weight": 0.95,
            "category": "port",
        },
        {
            "name": "Patrick Terminals",
            "lat": -33.9715,
            "lon": 151.2100,
            "weight": 0.95,
            "category": "port",
        },
        {
            "name": "DP World Terminal",
            "lat": -33.9730,
            "lon": 151.2230,
            "weight": 0.95,
            "category": "port",
        },
        {
            "name": "Naval / RAN Proximity Zone",
            "lat": -33.9820,
            "lon": 151.2280,
            "weight": 1.0,
            "category": "naval",
        },
        {
            "name": "Botany Bay Shipping Approaches",
            "lat": -33.9910,
            "lon": 151.2392,
            "weight": 0.7,
            "category": "harbour",
        },
        {
            "name": "Port Botany General Area",
            "lat": -33.9760,
            "lon": 151.2180,
            "weight": 0.9,
            "category": "port",
        },
        {
            "name": "Botany Bay Harbour Waters",
            "lat": -33.9890,
            "lon": 151.2350,
            "weight": 0.85,
            "category": "harbour",
        },
    ]
