<!-- Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work -->
# Vessel Logistics

Unified shipping, receiving, and navigation systems for watercraft from large freight carriers down to speed boats.

## Layout
- `Core/` — shared interfaces, telemetry, event bus
- `Systems/Shipping/` — manifest, load planning, dock scheduling
- `Systems/Receiving/` — inbound manifest verification, offload sequencing
- `Systems/Navigation/` — route planning, collision avoidance, autopilot presets
- `Vessels/Freight/` — freight carrier profiles
- `Vessels/Ferry/` — ferry profiles
- `Vessels/Speedboat/` — speedboat profiles
- `tests/` — regression and scenario tests
- `docs/` — design notes

## Build
TBD based on backend choice; current scaffold uses JSON schemas + Python toolchain.
