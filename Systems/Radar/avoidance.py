#!/usr/bin/env python3
# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
"""Anticrash avoidance planner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from Systems.Radar.radar_service import RadarService, Vec3, Ping


class AnticrashSystem:
    def __init__(self, radar: Optional[RadarService] = None) -> None:
        self.radar = radar or RadarService()

    def evaluate(self, position: Vec3, heading_deg: float, speed_knots: float, intent: str = "transit") -> dict:
        if not self.radar.self_vessel_id:
            return {"status": "no_self_vessel"}
        self.radar.broadcast(position, heading_deg, speed_knots, intent=intent)
        advice = self.radar.avoidance_advice()
        return {
            "status": "ok",
            "broadcast": _asdict(self.radar.pings[-1]) if self.radar.pings else None,
            "visible_count": len(self.radar.visible_pings()),
            "advice": advice
        }


def _asdict(ping: Ping) -> dict:
    return {
        "vessel_id": ping.vessel_id,
        "vessel_class": ping.vessel_class,
        "timestamp_iso": ping.timestamp_iso,
        "position": {"x": ping.position.x, "y": ping.position.y, "z": ping.position.z},
        "heading_deg": ping.heading_deg,
        "speed_knots": ping.speed_knots,
        "range_m": ping.range_m,
        "intent": ping.intent,
    }


def main() -> int:
    radar = RadarService()
    radar.set_self("SB_ZEN_1", "speedboat")
    sys = AnticrashSystem(radar)
    result = sys.evaluate(Vec3(0.0, 0.0, 0.0), 45.0, 35.0)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
