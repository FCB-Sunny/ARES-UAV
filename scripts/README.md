# Demo / launch scripts (Phase 0)

These are the **only** runtime scripts you need for the current takeoff/land demo.

| File | Role |
|------|------|
| `start_sitl_gui.sh` | Starts Gazebo (3D window) + PX4 SITL inside WSL |
| `mavsdk_takeoff_land.py` | Arms, takes off, lands via MAVSDK |

**Usual way to run (Windows):** double-click `run_ares_demo.bat` in the repo root.

Do **not** edit PX4/ROS/Gazebo source under WSL for ARES work — those are installed tools. Future ARES application code will live in `control/`, `autonomy/`, etc.
