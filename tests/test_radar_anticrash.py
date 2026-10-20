#!/usr/bin/env python3
# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
"""Radar + anticrash smoke tests."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from Systems.Radar.radar_service import RadarService, Vec3, Ping


def test_radar_sees_multiple_vessels():
    radar = RadarService()
    radar.enable_multi_mode()
    radar.ingest_ping(Ping("MV_ZEN_FREIGHT", "freight_carrier", "2026-08-11T00:10:00Z", Vec3(0.0, 0.0, 0.0), 87.0, 18.5, 12000.0))
    radar.ingest_ping(Ping("MV_ZEN_FERRY", "ferry", "2026-08-11T00:10:02Z", Vec3(108.0, 0.0, -42.0), 265.0, 22.0, 9500.0))
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    visible = radar.visible_pings()
    assert len(visible) == 1
    assert visible[0].vessel_id == "MV_ZEN_FERRY"


def test_nearest_visible():
    radar = RadarService()
    radar.enable_multi_mode()
    radar.ingest_ping(Ping("MV_ZEN_FREIGHT", "freight_carrier", "2026-08-11T00:10:00Z", Vec3(0.0, 0.0, 0.0), 0.0, 0.0, 1000.0))
    radar.ingest_ping(Ping("MV_ZEN_FERRY", "ferry", "2026-08-11T00:10:01Z", Vec3(10.0, 0.0, 0.0), 180.0, 20.0, 1000.0))
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    nearest = radar.nearest_visible()
    assert nearest is not None
    assert nearest.vessel_id == "MV_ZEN_FERRY"


def test_avoidance_triggered_within_cpa():
    radar = RadarService()
    radar.enable_multi_mode()
    radar.ingest_ping(Ping("MV_ZEN_FREIGHT", "freight_carrier", "2026-08-11T00:10:00Z", Vec3(0.0, 0.0, 0.0), 0.0, 0.0, 1000.0))
    radar.ingest_ping(Ping("MV_ZEN_FERRY", "ferry", "2026-08-11T00:10:01Z", Vec3(50.0, 0.0, 0.0), 180.0, 20.0, 1000.0))
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    advice = radar.avoidance_advice()
    assert advice is not None
    assert advice["cpa_m"] <= 200.0


def test_anticrash_system_evaluate():
    from Systems.Radar.avoidance import AnticrashSystem
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
