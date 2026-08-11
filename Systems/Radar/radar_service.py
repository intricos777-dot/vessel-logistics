#!/usr/bin/env python3
"""Shared radar ping broadcast service."""
from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass, field, asdict
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

    def set_self(self, vessel_id: str, vessel_class: str) -> None:
        self.self_vessel_id = vessel_id
        self.vessel_class = vessel_class

    def broadcast(self, position: Vec3, heading_deg: float, speed_knots: float, intent: str = "transit") -> Ping:
        ping = Ping(
            vessel_id=self.self_vessel_id or "unknown",
            vessel_class=getattr(self, "vessel_class", "speedboat"),
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
        cpa = self.cpa_m(Ping(self.self_vessel_id or "self", getattr(self, "vessel_class", "speedboat"), "", Vec3(), 0.0, 0.0, 0.0), nearest)
        if cpa > self.policy.get("cpa_limit_m", 200):
            return None
        reaction = self.policy.get("reaction", {}).get(getattr(self, "vessel_class", "speedboat"), "course_offset+fast")
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
