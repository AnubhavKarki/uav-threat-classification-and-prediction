"""
Logging: terminal output and TXT file export.
"""

from typing import List

from simulation.drone import Drone


def write_logs(
    drones: List[Drone],
    log_file: str,
    metrics_log_file: str,
) -> None:
    """Write main drone log and metrics log to TXT files and terminal."""
    with (
        open(log_file, "w", encoding="utf-8") as f_main,
        open(metrics_log_file, "w", encoding="utf-8") as f_metrics,
    ):
        header = "drone_id,timestamp,latitude,longitude,altitude,drone_type,step\n"
        f_main.write(header)

        metrics_header = (
            "drone_id,timestamp,latitude,longitude,drone_type,step,"
            "in_risk_zone,flight_deviation_deg,hovering_duration_s,"
            "sensor_orientation_deg,sensor_target,heading_deg,ground_speed_mps,"
            "threat_time_s\n"
        )
        f_metrics.write(metrics_header)

        for drone in drones:
            for pos in drone.positions:
                lat = pos["lat"]
                lon = pos["lon"]
                altitude = pos["altitude"]
                ts_str = pos["timestamp"]
                step = pos["step"]

                log_line = (
                    f"Drone ID: {drone.id}, "
                    f"Type: {drone.role}, "
                    f"Step: {step}, "
                    f"Timestamp: {ts_str}, "
                    f"Latitude: {lat}, Longitude: {lon}, Altitude: {altitude}"
                )
                print(log_line)

                csv_line = (
                    f"{drone.id},{ts_str},{lat},{lon},{altitude},"
                    f"{drone.role},{step}\n"
                )
                f_main.write(csv_line)

                metrics_line = (
                    f"{drone.id},{ts_str},{lat},{lon},{drone.role},{step},"
                    f"{int(pos['in_risk_zone'])},"
                    f"{round(pos['flight_deviation_deg'], 2)},"
                    f"{round(pos['hovering_duration_s'], 1)},"
                    f"{'' if pos['sensor_orientation_deg'] is None else round(pos['sensor_orientation_deg'], 1)},"
                    f"{'' if pos['sensor_target'] is None else pos['sensor_target']},"
                    f"{'' if pos['heading_deg'] is None else round(pos['heading_deg'], 1)},"
                    f"{round(pos['ground_speed_mps'], 2)},"
                    f"{round(pos['threat_time_s'], 1)}\n"
                )
                f_metrics.write(metrics_line)
