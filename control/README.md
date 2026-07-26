# `control/` — Flight control interface (Phase 1)

**Responsibility:** talk to one PX4 vehicle through MAVSDK.

You do **not** need to understand Gazebo or `gz_bridge` to work here.
Those are below this layer.

## Files

| File | Role |
|------|------|
| `vehicle.py` | Thin wrapper: connect / arm / takeoff / goto / land |
| `mission_runner.py` | Orchestrates a `MissionPlan` on a `Vehicle` |

## Dependency direction (important)

```
scripts/run_waypoint_mission.py
        → control.mission_runner
        → control.vehicle          (MAVSDK only lives here)
        → interfaces.mission       (data only — no MAVSDK)
```

Never import `mavsdk` from `interfaces/` or from mission JSON loaders.

## Run (SITL already up)

Inside WSL:

```bash
cd /mnt/c/Users/a/Projects/ARES-UAV
source ~/ares-venv/bin/activate
python3 scripts/run_waypoint_mission.py missions/square_demo.json
```

Or from Windows: `run_ares_demo.bat` (starts sim + this mission).
