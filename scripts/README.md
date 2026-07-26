# Demo / launch scripts

| File | Role |
|------|------|
| `start_sitl_gui.sh` | Gazebo (3D) + PX4 SITL inside WSL |
| `run_waypoint_mission.py` | **Phase 1** — load mission JSON, fly waypoints |
| `mavsdk_takeoff_land.py` | Phase 0 smoke test (arm → takeoff → land only) |

**Usual way (Windows):** `run_ares_demo.bat` → starts sim + Phase 1 square mission.

ARES application logic lives in `control/` and `interfaces/`, not in PX4/Gazebo source.
