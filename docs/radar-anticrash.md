# Radar Anticrash System

Every vessel broadcasts a ping with position, heading, speed, and intent. Other vessels ingest all visible pings, compute closest point of approach (CPA), and trigger avoidance advice when another vessel is within `cpa_limit_m`.

Reaction rules:
- `speedboat` → `course_offset+fast`
- `ferry` → `course_offset+notify`
- `freight_carrier` → `course_offset+slow`

Run:
```bash
python3 Systems/Radar/radar_service.py
python3 Systems/Radar/avoidance.py
python3 tests/test_radar_anticrash.py
```
