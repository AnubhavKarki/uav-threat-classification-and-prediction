"""
Drone dataclass: single source of truth for UAV state.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Drone:
    """Represents a simulated UAV with its trajectory history."""

    id: str
    role: str  # "inspection" or "threat"
    trajectory_id: int
    positions: List[Dict[str, Any]] = field(default_factory=list)
