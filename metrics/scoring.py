"""
Unified dynamic threat score: risk zone time, hovering, deviation, sensor fixation.

Used for telemetry ranking and threat headline. No hard-coding of threat drone.
"""


def _compute_threat_score(pos: dict) -> float:
    """
    Combine risk zone time, hovering, flight deviation, sensor fixation
    into a single threat score.
    """
    score = 0.0

    if pos.get("in_risk_zone"):
        score += pos.get("threat_time_s", 0) * 0.5
    score += pos.get("hovering_duration_s", 0) * 0.3
    score += pos.get("flight_deviation_deg", 0) * 0.02
    if pos.get("sensor_target"):
        score += 2.0

    return score


def compute_threat_scores(drones: list) -> None:
    """
    Attach threat_score to each position for ranking.
    Modifies drone.positions in place.
    """
    for drone in drones:
        for pos in drone.positions:
            pos["threat_score"] = _compute_threat_score(pos)
