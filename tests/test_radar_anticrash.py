#!/usr/bin/env python3
"""Radar + anticrash smoke tests."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from Systems.Radar.radar_service import RadarService, Vec3, Ping
from Systems.Radar.avoidance import AnticrashSystem


def test_radar_sees_multiple_vessels():
    radar = RadarService()
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    radar.broadcast(Vec3(0.0, 0.0, 0.0), 87.0, 18.5)
    radar.broadcast(Vec3(100.0, 0.0, -40.0), 265.0, 22.0)
    assert len(radar.visible_pings()) == 1


def test_nearest_visible():
    radar = RadarService()
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    radar.broadcast(Vec3(0.0, 0.0, 0.0), 0.0, 0.0)
    radar.broadcast(Vec3(10.0, 0.0, 0.0), 180.0, 20.0)
    nearest = radar.nearest_visible()
    assert nearest is not None
    assert nearest.vessel_id != "MV_ZEN_FREIGHT"


def test_avoidance_triggered_within_cpa():
    radar = RadarService()
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    radar.broadcast(Vec3(0.0, 0.0, 0.0), 0.0, 0.0)
    radar.broadcast(Vec3(50.0, 0.0, 0.0), 180.0, 20.0)
    advice = radar.avoidance_advice()
    assert advice is not None
    assert advice["cpa_m"] <= 200.0


def test_anticrash_system_evaluate():
    radar = RadarService()
    radar.set_self("SB_ZEN_1", "speedboat")
    sys = AnticrashSystem(radar)
    result = sys.evaluate(Vec3(0.0, 0.0, 0.0), 45.0, 35.0)
    assert result["status"] == "ok"
    assert "visible_count" in result


if __name__ == "__main__":
    sys.exit(0 if all([
        test_radar_sees_multiple_vessels(),
        test_nearest_visible(),
        test_avoidance_triggered_within_cpa(),
        test_anticrash_system_evaluate(),
    ]) else 1)
