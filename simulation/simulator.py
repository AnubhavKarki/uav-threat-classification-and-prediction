"""
Simulation orchestration: drones, trajectories, metrics, exporters.

No UI or file I/O logic here; delegates to export modules.
"""

import datetime
import random

from config.constants import (
    NUM_DRONES,
    NUM_STEPS,
    ALTITUDE_MIN,
    ALTITUDE_MAX,
    LOG_FILE,
    MAP_FILE,
    METRICS_LOG_FILE,
    THREAT_JSON_FILE,
)
from config.port_botany import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX
from core.utils import generate_drone_id, generate_altitude, base_time
from simulation.drone import Drone
from simulation.trajectories import (
    trajectory_from_north_to_ship,
    trajectory_from_south_to_ship,
    trajectory_from_west_to_cranes,
    trajectory_from_east_to_ship2,
)
from simulation.movement import step_threat_drone
from metrics.risk import is_high_risk_zone
from metrics.behavior import enrich_positions_with_metrics
from metrics.scoring import compute_threat_scores
from export.logger import write_logs
from export.json_export import export_threat_telemetry
from export.map_builder import build_map


def _create_drones() -> list[Drone]:
    """Create initial drone fleet."""
    drones = []
    for i in range(NUM_DRONES):
        drones.append(
            Drone(
                id=generate_drone_id(),
                role="threat" if i == NUM_DRONES - 1 else "inspection",
                trajectory_id=i,
                positions=[],
            )
        )
    return drones


def _run_simulation_loop(drones: list[Drone]) -> None:
    """Advance all drones through NUM_STEPS."""
    start_time = base_time()
    threat_heading_deg = random.uniform(0.0, 360.0)
    threat_speed_mps = random.uniform(10.0, 14.0)
    threat_lat = random.uniform(LAT_MIN, LAT_MAX)
    threat_lon = random.uniform(LON_MIN, LON_MAX)

    for step in range(NUM_STEPS):
        current_time = start_time + datetime.timedelta(seconds=step)
        ts_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        for idx, drone in enumerate(drones):
            if drone.role == "inspection":
                if drone.trajectory_id == 0:
                    lat, lon = trajectory_from_north_to_ship(step, NUM_STEPS)
                elif drone.trajectory_id == 1:
                    lat, lon = trajectory_from_south_to_ship(step, NUM_STEPS)
                elif drone.trajectory_id == 2:
                    lat, lon = trajectory_from_west_to_cranes(step, NUM_STEPS)
                else:
                    lat, lon = trajectory_from_east_to_ship2(step, NUM_STEPS)
            else:
                if step > 0:
                    threat_lat, threat_lon, threat_heading_deg, threat_speed_mps = (
                        step_threat_drone(
                            threat_lat,
                            threat_lon,
                            threat_heading_deg,
                            threat_speed_mps,
                            step,
                        )
                    )
                lat, lon = threat_lat, threat_lon

            altitude = generate_altitude(ALTITUDE_MIN, ALTITUDE_MAX)
            lat = round(lat, 4)
            lon = round(lon, 4)
            altitude = round(altitude, 4)

            drone.positions.append(
                {
                    "lat": lat,
                    "lon": lon,
                    "altitude": altitude,
                    "timestamp": ts_str,
                    "step": step,
                }
            )


def run_simulation() -> None:
    """
    Run full simulation: drones, metrics, logs, map, JSON export.
    """
    drones = _create_drones()
    _run_simulation_loop(drones)

    enrich_positions_with_metrics(drones)
    compute_threat_scores(drones)

    write_logs(
        drones,
        LOG_FILE,
        METRICS_LOG_FILE,
    )

    build_map(drones, MAP_FILE)

    threat_drone = next((d for d in drones if d.role == "threat"), None)
    if threat_drone:
        export_threat_telemetry(threat_drone, THREAT_JSON_FILE)

    print(f"\nMap saved to {MAP_FILE}")
    print(f"Log saved to {LOG_FILE}")
