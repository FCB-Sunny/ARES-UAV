# `simulation/` — Worlds and sim configs (ARES-owned)

**Responsibility:** Gazebo worlds / assets for demos. Not PX4 source.

## Worlds

| File | Role |
|------|------|
| `worlds/ares_navigate.sdf` | Phase 2: default PX4 plugins + visible cylinder obstacle |

## Frame convention (important)

Gazebo world frame is **ENU**:

| Planner (`north_m`, `east_m`) | Gazebo pose |
|-------------------------------|-------------|
| east | **x** |
| north | **y** |
| up | **z** |

`missions/navigate_demo.json` obstacle `(N=10, E=8, r=4)` → cylinder at pose `8 10 4` (radius 4, height 8).

Keep JSON and SDF in sync when you move the obstacle.

## Used by

`scripts/start_sitl_gui.sh` launches this world for the one-click demo.
