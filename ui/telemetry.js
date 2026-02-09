/**
 * UAV Telemetry Panel – Client-side logic.
 *
 * Requirements:
 * - Rank ALL drones each timestep by dynamic threat score
 * - Headline shows highest current threat
 * - No assumption that role === "threat"
 *
 * Expects globals: DRONES, droneLabels, maxSteps, metricsDiv
 */

(function () {
  'use strict';

  function getOrderedByThreatScore(stepIdx) {
    return DRONES.map(function (_, i) {
      return i;
    }).sort(function (a, b) {
      const pa = DRONES[a].positions[stepIdx] || {};
      const pb = DRONES[b].positions[stepIdx] || {};
      const sa = typeof pa.threat_score === 'number' ? pa.threat_score : 0;
      const sb = typeof pb.threat_score === 'number' ? pb.threat_score : 0;
      return sb - sa;
    });
  }

  function getThreatHeadline(orderedIdx, stepIdx) {
    const topIdx = orderedIdx[0];
    const topDrone = DRONES[topIdx];
    const topPos = topDrone && topDrone.positions[stepIdx];
    let headline = 'Threat status: No active threat detected.';

    if (topPos && (topPos.threat_score || 0) > 2) {
      const tt = typeof topPos.threat_time_s === 'number' ? topPos.threat_time_s : 0;
      const inRisk = !!topPos.in_risk_zone;
      let level = 'LOW';
      let action = 'Monitoring from command centre.';

      if (inRisk && tt >= 5 && tt < 15) {
        level = 'ELEVATED';
        action = 'Dispatching friendly drones to shadow and inspect behaviour.';
      } else if (inRisk && tt >= 15 && tt < 30) {
        level = 'HIGH';
        action = 'Authorising intercept; EW / jamming or non‑kinetic effects.';
      } else if (inRisk && tt >= 30) {
        level = 'CRITICAL';
        action = 'Air strike / hard‑kill option on table; neutralise immediately.';
      } else if ((topPos.threat_score || 0) > 5) {
        level = 'ELEVATED';
        action = 'Investigating suspicious behaviour.';
      }
      headline = 'Highest threat: ' + topDrone.id + ' – ' + level + '. ' + action;
    }
    return headline;
  }

  window.telemetry = {
    rankDrones: getOrderedByThreatScore,
    getThreatHeadline: getThreatHeadline,
  };
})();
