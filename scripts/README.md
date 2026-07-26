# Demo / launch scripts

| File | Role |
|------|------|
| `start_sitl_gui.sh` | Gazebo (3D) + PX4 SITL inside WSL |
| `run_waypoint_mission.py` | **Phase 1** — load mission JSON, fly waypoints |
| `run_planned_mission.py` | **Phase 2** — plan from navigation JSON, then fly |
| `mavsdk_takeoff_land.py` | Phase 0 smoke test (arm → takeoff → land only) |

**Usual way (Windows):** `run_ares_demo.bat` → starts sim + Phase 1 square mission.

Phase 2 (SITL already up): `python scripts/run_planned_mission.py missions/navigate_demo.json` (inside WSL with venv), or `--plan-only` without sim.

ARES application logic lives in `control/`, `autonomy/`, and `interfaces/`, not in PX4/Gazebo source.
