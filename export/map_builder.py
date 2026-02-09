"""
Build animated Leaflet HTML map for UAV simulation.

Heatmap: dark, red-dominant, larger radius.
Polylines reset when simulation loops.
"""

import json

from config.port_botany import (
    PORT_BOTANY_CENTER_LAT,
    PORT_BOTANY_CENTER_LON,
    SHIP_1,
    SHIP_2,
    CRANE_1,
    CRANE_2,
)
from metrics.risk import generate_risk_heat_points


def build_map(drones: list, output_path: str) -> None:
    """Generate animated Leaflet map HTML."""
    colors = ["blue", "green", "orange", "purple", "red"]

    js_drones = []
    for idx, drone in enumerate(drones):
        positions_js = []
        for pos in drone.positions:
            positions_js.append(
                {
                    "lat": pos["lat"],
                    "lon": pos["lon"],
                    "altitude": pos["altitude"],
                    "timestamp": pos["timestamp"],
                    "step": pos["step"],
                    "in_risk_zone": pos["in_risk_zone"],
                    "flight_deviation_deg": pos["flight_deviation_deg"],
                    "hovering_duration_s": pos["hovering_duration_s"],
                    "sensor_orientation_deg": pos["sensor_orientation_deg"],
                    "sensor_target": pos["sensor_target"],
                    "heading_deg": pos["heading_deg"],
                    "ground_speed_mps": pos["ground_speed_mps"],
                    "threat_time_s": pos["threat_time_s"],
                    "threat_score": pos.get("threat_score", 0),
                }
            )

        js_drones.append(
            {
                "id": drone.id,
                "type": drone.role,
                "color": colors[idx % len(colors)],
                "positions": positions_js,
            }
        )

    heat_points = generate_risk_heat_points()

    drones_json = json.dumps(js_drones)
    heat_json = json.dumps(heat_points)

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Port Botany UAV Threat Classification</title>
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"
  />
  <style>
    html, body, #map {{
      height: 100%;
      margin: 0;
      padding: 0;
    }}
    .legend {{
      background: white;
      padding: 6px 8px;
      font: 14px/16px Arial, Helvetica, sans-serif;
      box-shadow: 0 0 15px rgba(0,0,0,0.2);
      border-radius: 5px;
    }}
    .legend h4 {{
      margin: 0 0 5px;
    }}
    .legend span {{
      display: inline-block;
      width: 12px;
      height: 12px;
      margin-right: 5px;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="sidebar" style="position:absolute;top:10px;right:10px;z-index:1000;background:white;padding:10px 12px;border-radius:6px;box-shadow:0 0 10px rgba(0,0,0,0.25);max-width:340px;font-family:Arial, sans-serif;font-size:13px;">
    <h3 style="margin:0 0 6px 0;font-size:16px;">Drone Telemetry</h3>
    <div id="metrics-summary" style="max-height:260px;overflow-y:auto;"></div>
    <div style="margin-top:6px;">
      <button id="btn-pause" style="margin-right:4px;">Pause</button>
      <button id="btn-play">Play</button>
      <label style="margin-left:8px;">Speed:
        <input id="speed-range" type="range" min="100" max="800" value="300" />
      </label>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.heat/dist/leaflet-heat.js"></script>
  <script>
    const DRONES = {drones_json};
    const HEAT_POINTS = {heat_json};
    const CENTER = [{PORT_BOTANY_CENTER_LAT}, {PORT_BOTANY_CENTER_LON}];

    const map = L.map('map').setView(CENTER, 12);

    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    // Risk heatmap: fixed radius/blur — no changes on zoom (avoids new markers appearing)
    const heatData = HEAT_POINTS.map(p => [p.lat, p.lon, p.intensity * 1.5]);
    const heatLayer = L.heatLayer(heatData, {{
      radius: 14,
      blur: 12,
      maxZoom: 18,
      minOpacity: 0.5,
      max: 2.0,
      gradient: {{ 0.0: '#330000', 0.4: '#990000', 0.7: '#cc0000', 1.0: '#ff0000' }}
    }}).addTo(map);

    // Ships & cranes (static markers)
    L.marker([{SHIP_1[0]}, {SHIP_1[1]}]).addTo(map).bindPopup('SHIP 1 - Inspected');
    L.marker([{SHIP_2[0]}, {SHIP_2[1]}]).addTo(map).bindPopup('SHIP 2 - Threat Orbit');
    L.marker([{CRANE_1[0]}, {CRANE_1[1]}]).addTo(map).bindPopup('CRANE 1');
    L.marker([{CRANE_2[0]}, {CRANE_2[1]}]).addTo(map).bindPopup('CRANE 2');

    const droneMarkers = [];
    const dronePolylines = [];
    const droneLabels = [];

    DRONES.forEach((drone) => {{
      const first = drone.positions[0];
      const marker = L.circleMarker([first.lat, first.lon], {{
        radius: 6,
        color: drone.color,
        fillColor: drone.color,
        fillOpacity: 0.9,
        weight: 2
      }}).addTo(map);
      marker.bindPopup(drone.id + ' (' + (drone.type === 'threat' ? 'THREAT' : 'INSPECTION') + ')');

      const poly = L.polyline([[first.lat, first.lon]], {{
        color: drone.color,
        weight: 3,
        opacity: 0.8
      }}).addTo(map);

      droneMarkers.push(marker);
      dronePolylines.push(poly);
      droneLabels.push((drone.type === 'threat' ? 'Threat' : 'Inspection') + ' – ' + drone.id);
    }});

    const allCoords = [];
    DRONES.forEach((drone) => {{
      drone.positions.forEach((p) => allCoords.push([p.lat, p.lon]));
    }});
    map.fitBounds(allCoords);

    let step = 0;
    const maxSteps = DRONES[0].positions.length;
    let intervalMs = 300;
    let timerId = null;

    const metricsDiv = document.getElementById('metrics-summary');
    const pauseBtn = document.getElementById('btn-pause');
    const playBtn = document.getElementById('btn-play');
    const speedRange = document.getElementById('speed-range');

    function renderMetrics(stepIdx) {{
      let html = '<div style="font-weight:bold;margin-bottom:4px;">Step ' + (stepIdx + 1) + '/' + maxSteps + '</div>';

      // Rank ALL drones by threat_score; headline = highest current threat (no role assumption)
      const orderedIdx = DRONES.map((_, i) => i).sort((a, b) => {{
        const pa = DRONES[a].positions[stepIdx] || {{}};
        const pb = DRONES[b].positions[stepIdx] || {{}};
        const sa = typeof pa.threat_score === 'number' ? pa.threat_score : 0;
        const sb = typeof pb.threat_score === 'number' ? pb.threat_score : 0;
        return sb - sa;
      }});

      const topDrone = DRONES[orderedIdx[0]];
      const topPos = topDrone && topDrone.positions[stepIdx];
      let threatHeadline = 'Threat status: No active threat detected.';
      if (topPos && (topPos.threat_score || 0) > 2) {{
        const tt = typeof topPos.threat_time_s === 'number' ? topPos.threat_time_s : 0;
        const inRisk = !!topPos.in_risk_zone;
        let level = 'LOW';
        let action = 'Monitoring from command centre.';
        if (inRisk && tt >= 5 && tt < 15) {{
          level = 'ELEVATED';
          action = 'Dispatching friendly drones to shadow and inspect behaviour.';
        }} else if (inRisk && tt >= 15 && tt < 30) {{
          level = 'HIGH';
          action = 'Authorising intercept; EW / jamming or non‑kinetic effects.';
        }} else if (inRisk && tt >= 30) {{
          level = 'CRITICAL';
          action = 'Air strike / hard‑kill option on table; neutralise immediately.';
        }} else if ((topPos.threat_score || 0) > 5) {{
          level = 'ELEVATED';
          action = 'Investigating suspicious behaviour.';
        }}
        threatHeadline = 'Highest threat: ' + topDrone.id + ' – ' + level + '. ' + action;
      }}

      html += '<div style="margin-bottom:8px;padding:6px 8px;background:#111;color:#fff;border-radius:4px;font-size:12px;">' + threatHeadline + '</div>';

      orderedIdx.forEach((idx) => {{
        const drone = DRONES[idx];
        const pos = drone.positions[stepIdx];
        if (!pos) return;
        const riskBadge = pos.in_risk_zone
          ? '<span style="color:#b30000;font-weight:bold;">HIGH‑RISK ZONE</span>'
          : '<span style="color:#555;">Normal</span>';
        const sensorTarget = pos.sensor_target || '—';
        const threatTime = typeof pos.threat_time_s === 'number' ? pos.threat_time_s.toFixed(1) : '0.0';
        const sensorOrientation = pos.sensor_orientation_deg == null ? '—' : pos.sensor_orientation_deg.toFixed(1) + '°';
        html += '<div style="margin-bottom:6px;border-bottom:1px solid #eee;padding-bottom:4px;">' +
          '<div style="font-weight:bold;">' + droneLabels[idx] + '</div>' +
          '<div>Status: ' + riskBadge + '</div>' +
          '<div>Lat/Lon: ' + pos.lat.toFixed(5) + ', ' + pos.lon.toFixed(5) + '</div>' +
          '<div>Alt: ' + pos.altitude.toFixed(1) + ' m</div>' +
          '<div>Flight deviation: ' + pos.flight_deviation_deg.toFixed(1) + '°</div>' +
          '<div>Hovering duration: ' + pos.hovering_duration_s.toFixed(1) + ' s</div>' +
          '<div>ThreatArea_Time: ' + threatTime + ' s</div>' +
          '<div>Threat score: ' + (pos.threat_score != null ? pos.threat_score.toFixed(1) : '—') + '</div>' +
          '<div>Sensor target: ' + sensorTarget + '</div>' +
          '<div>Sensor orientation: ' + sensorOrientation + '</div>' +
          '</div>';
      }});
      metricsDiv.innerHTML = html;
    }}

    function resetPolylines() {{
      DRONES.forEach((drone, idx) => {{
        const first = drone.positions[0];
        dronePolylines[idx].setLatLngs([[first.lat, first.lon]]);
      }});
    }}

    function update() {{
      step++;
      if (step >= maxSteps) {{
        step = 0;
        resetPolylines();
      }}

      DRONES.forEach((drone, idx) => {{
        const pos = drone.positions[step];
        if (!pos) return;
        const latlng = [pos.lat, pos.lon];
        droneMarkers[idx].setLatLng(latlng);
        const isRisk = !!pos.in_risk_zone;
        droneMarkers[idx].setStyle({{
          radius: isRisk ? 8 : 6,
          weight: isRisk ? 3 : 2,
          color: drone.color,
          fillColor: drone.color,
        }});
        dronePolylines[idx].addLatLng(latlng);
      }});
      renderMetrics(step);
    }}

    function startAnimation() {{
      if (timerId !== null) return;
      timerId = setInterval(update, intervalMs);
    }}

    function stopAnimation() {{
      if (timerId !== null) {{
        clearInterval(timerId);
        timerId = null;
      }}
    }}

    pauseBtn.onclick = () => stopAnimation();
    playBtn.onclick = () => startAnimation();
    speedRange.oninput = (e) => {{
      intervalMs = Number(e.target.value);
      if (timerId !== null) {{
        stopAnimation();
        startAnimation();
      }}
    }};

    renderMetrics(step);
    startAnimation();

    const legend = L.control({{ position: 'bottomright' }});
    legend.onAdd = function () {{
      const div = L.DomUtil.create('div', 'legend');
      div.innerHTML = '<h4>Drones over Port Botany</h4>' +
        '<div><span style="background: red;"></span>Threat drone</div>' +
        '<div><span style="background: blue;"></span>Inspection drones</div>';
      return div;
    }};
    legend.addTo(map);
  </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
