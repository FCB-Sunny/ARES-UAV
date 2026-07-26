# Demo / launch scripts

| File | Role |
|------|------|
| `start_sitl_gui.sh` | Gazebo (3D) + PX4 SITL inside WSL |
| `run_waypoint_mission.py` | **Phase 1** — load mission JSON, fly waypoints |
| `run_planned_mission.py` | **Phase 2** — plan from navigation JSON, then fly |
| `mavsdk_takeoff_land.py` | Phase 0 smoke test (arm → takeoff → land only) |

**Usual way (Windows):** double-click `run_ares_demo.bat` → Gazebo world with cylinder + PX4 + Phase 2 planned flight.

Avoidance check (no sim): `python scripts/check_plan_avoidance.py missions/navigate_demo.json`

ARES application logic lives in `control/`, `autonomy/`, and `interfaces/`. Worlds live in `simulation/`.
