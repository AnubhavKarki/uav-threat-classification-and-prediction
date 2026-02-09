"""
Inspection drone trajectories over Port Botany.

Deterministic paths that stay tightly over infrastructure.
"""

from typing import Tuple

from config.port_botany import (
    PORT_BOTANY_CENTER_LAT,
    PORT_BOTANY_CENTER_LON,
    LAT_MIN,
    LAT_MAX,
    LON_MIN,
    LON_MAX,
    SHIP_1,
    SHIP_2,
    CRANE_1,
    CRANE_2,
)
from core.geo import clamp


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def trajectory_from_north_to_ship(step: int, num_steps: int) -> Tuple[float, float]:
    """
    Drone 1: Approaches from NORTH into Port Botany.
    Flies over CRANE_1 then inspects SHIP_1.
    """
    mid = num_steps // 2
    if step <= mid:
        t = step / mid
        start_lat, start_lon = LAT_MAX + 0.01, PORT_BOTANY_CENTER_LON
        lat = lerp(start_lat, CRANE_1[0], t)
        lon = lerp(start_lon, CRANE_1[1], t)
    else:
        t = (step - mid) / (num_steps - 1 - mid)
        lat = lerp(CRANE_1[0], SHIP_1[0], t)
        lon = lerp(CRANE_1[1], SHIP_1[1], t)
    return clamp(lat, LAT_MIN, LAT_MAX), clamp(lon, LON_MIN, LON_MAX)


def trajectory_from_south_to_ship(step: int, num_steps: int) -> Tuple[float, float]:
    """
    Drone 2: Approaches from SOUTH.
    Inspects SHIP_1 then CRANE_2.
    """
    mid = num_steps // 2
    if step <= mid:
        t = step / mid
        start_lat, start_lon = LAT_MIN - 0.01, PORT_BOTANY_CENTER_LON + 0.01
        lat = lerp(start_lat, SHIP_1[0], t)
        lon = lerp(start_lon, SHIP_1[1], t)
    else:
        t = (step - mid) / (num_steps - 1 - mid)
        lat = lerp(SHIP_1[0], CRANE_2[0], t)
        lon = lerp(SHIP_1[1], CRANE_2[1], t)
    return clamp(lat, LAT_MIN, LAT_MAX), clamp(lon, LON_MIN, LON_MAX)


def trajectory_from_west_to_cranes(step: int, num_steps: int) -> Tuple[float, float]:
    """
    Drone 3: Approaches from WEST.
    Flies along quay: CRANE_1 then CRANE_2.
    
    
    """
    mid = num_steps // 2
    if step <= mid:
        t = step / mid
        start_lat, start_lon = PORT_BOTANY_CENTER_LAT, LON_MIN - 0.01
        lat = lerp(start_lat, CRANE_1[0], t)
        lon = lerp(start_lon, CRANE_1[1], t)
    else:
        t = (step - mid) / (num_steps - 1 - mid)
        lat = lerp(CRANE_1[0], CRANE_2[0], t)
        lon = lerp(CRANE_1[1], CRANE_2[1], t)
    return clamp(lat, LAT_MIN, LAT_MAX), clamp(lon, LON_MIN, LON_MAX)


def trajectory_from_east_to_ship2(step: int, num_steps: int) -> Tuple[float, float]:
    """
    Drone 4: Approaches from EAST.
    Performs short inspection run across SHIP_2.
    """
    t = step / (num_steps - 1)
    start_lat, start_lon = PORT_BOTANY_CENTER_LAT - 0.005, LON_MAX + 0.01
    end_lat, end_lon = SHIP_2
    lat = lerp(start_lat, end_lat, t)
    lon = lerp(start_lon, end_lon, t)
    return clamp(lat, LAT_MIN, LAT_MAX), clamp(lon, LON_MIN, LON_MAX)
