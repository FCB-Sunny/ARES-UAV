# `autonomy/` — Path planning (Phase 2)

**Responsibility:** turn a navigation *request* into a flyable `MissionPlan`.

```
NavigationRequest  →  GridMap + A*  →  MissionPlan  →  control.mission_runner
```

`control/` stays unchanged. This package never imports MAVSDK.

## Files

| File | Role |
|------|------|
| `grid_map.py` | 2D occupancy grid from bounds + circle obstacles |
| `planner.py` | A* + path simplify → `MissionPlan` |

## Run (no sim — plan only)

```bash
cd /mnt/c/Users/a/Projects/ARES-UAV   # or Windows repo path
python -c "from interfaces.navigation import load_navigation; from autonomy.planner import plan_mission; p=plan_mission(load_navigation('missions/navigate_demo.json')); print(p)"
```

## Fly planned path (SITL up)

```bash
source ~/ares-venv/bin/activate
PYTHONPATH=. python3 scripts/run_planned_mission.py missions/navigate_demo.json
```

Obstacles here are **synthetic** (in JSON). Gazebo world obstacles come later.
