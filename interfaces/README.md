# `interfaces/` — Shared contracts

**Responsibility:** typed data shared across layers.

Phase 1 only defines a waypoint mission:

- `mission.py` — `Waypoint`, `MissionPlan`, `load_mission()`

Mission files live in repo root `missions/*.json` (examples / demos).
Validation happens when loading; invalid JSON fails closed before flight.
