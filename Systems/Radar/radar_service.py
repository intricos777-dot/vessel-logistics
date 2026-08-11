#!/usr/bin/env python3
"""Shared radar ping broadcast service."""
from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def dist_m(self, other: "Vec3") -> float:
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )


@dataclass
class Ping:
    vessel_id: str
    vessel_class: str
    timestamp_iso: str
    position: Vec3
    heading_deg: float
    speed_knots: float
    range_m: float
    intent: str = "transit"


class RadarService:
    def __init__(self, policy_path: str = "Systems/Radar/AnticrashPolicy.json") -> None:
        self.policy = json.loads((REPO_ROOT / policy_path).read_text())
        self.pings: List[Ping] = []
        self.self_vessel_id: Optional[str] = None
        self.vessel_class: str = "speedboat"
        self._multi_mode: bool = False

    def set_self(self, vessel_id: str, vessel_class: str) -> None:
        self.self_vessel_id = vessel_id
        self.vessel_class = vessel_class

    def enable_multi_mode(self) -> None:
        self._multi_mode = True

    def ingest_ping(self, ping: Ping) -> None:
        if not self._multi_mode and ping.vessel_id == self.self_vessel_id:
            return
        self.pings.append(ping)

    def broadcast(self, position: Vec3, heading_deg: float, speed_knots: float, intent: str = "transit") -> Ping:
        ping = Ping(
            vessel_id=self.self_vessel_id or "unknown",
            vessel_class=self.vessel_class,
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            position=position,
            heading_deg=heading_deg,
            speed_knots=speed_knots,
            range_m=self._estimate_range(speed_knots),
            intent=intent,
        )
        self.pings.append(ping)
        return ping

    def visible_pings(self) -> List[Ping]:
        if self._multi_mode:
            return [p for p in self.pings if self.self_vessel_id is None or p.vessel_id != self.self_vessel_id]
        return [p for p in self.pings if p.vessel_id != self.self_vessel_id]

    def nearest_visible(self) -> Optional[Ping]:
        visible = self.visible_pings()
        if not visible:
            return None
        return min(visible, key=lambda p: p.position.dist_m(Vec3()))

    def cpa_m(self, a: Ping, b: Ping) -> float:
        return a.position.dist_m(b.position)

    def avoidance_advice(self) -> Optional[dict]:
        nearest = self.nearest_visible()
        if not nearest:
            return None
        here = Vec3()
        cpa = self.cpa_m(Ping(
            vessel_id=self.self_vessel_id or "self",
            vessel_class=self.vessel_class,
            timestamp_iso="",
            position=here,
            heading_deg=0.0,
            speed_knots=0.0,
            range_m=0.0,
        ), nearest)
        if cpa > self.policy.get("cpa_limit_m", 200):
            return None
        reaction = self.policy.get("reaction", {}).get(self.vessel_class, "course_offset+fast")
        return {
            "nearest_vessel": nearest.vessel_id,
            "cpa_m": cpa,
            "reaction": reaction,
            "action": "adjust_course"
        }

    def _estimate_range(self, speed_knots: float) -> float:
        return max(500.0, min(20000.0, speed_knots * 400.0 + random.uniform(0, 800)))


def main() -> int:
    radar = RadarService()
    radar.set_self("MV_ZEN_FREIGHT", "freight_carrier")
    radar.broadcast(Vec3(0.0, 0.0, 0.0), 87.0, 18.5)
    radar.broadcast(Vec3(108.0, 0.0, -42.0), 265.0, 22.0, intent="transit")
    advice = radar.avoidance_advice()
    print(json.dumps({
        "visible_pings": len(radar.visible_pings()),
        "advice": advice
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
