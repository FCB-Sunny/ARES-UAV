# `interfaces/` — Shared contracts

**Responsibility:** typed data shared across layers.

| Module | Phase | Role |
|--------|-------|------|
| `mission.py` | 1 | Flyable waypoint plan (`MissionPlan`) |
| `navigation.py` | 2 | Start/goal/obstacles request (`NavigationRequest`) |

- Phase 1 scripts load a `MissionPlan` directly.
- Phase 2 planner converts `NavigationRequest` → `MissionPlan`.
- Validation happens on load; invalid JSON fails closed before flight.

