"""
General utilities for the UAV simulation.
"""

import random
import datetime


def generate_drone_id() -> str:
    """Generate a DJI-style drone ID."""
    return f"DJI-{random.randint(100000, 999999)}"


def generate_altitude(alt_min: float, alt_max: float) -> float:
    """Random altitude within a realistic drone range."""
    return round(random.uniform(alt_min, alt_max), 4)


def base_time() -> datetime.datetime:
    """Base timestamp for the simulation."""
    return datetime.datetime.now()
