# Phase 2 Architecture Review (living doc)

**Status:** Phase 2.1 in progress  
**Purpose:** Separate what **ARES** owns from what **PX4** and **Gazebo** own.

Related roadmap: Phase 2B in [`ROADMAP.md`](../ROADMAP.md).

---

## 1. Honest current pipeline (Phase 2A)

```
missions/*.json / NavigationRequest
        │
        ▼
autonomy/planner.py          ← ARES: global A* (static map)
        │ MissionPlan
        ▼
control/mission_runner.py    ← ARES: sequence arm/takeoff/goto/land
        │
        ▼
control/vehicle.py           ← ARES: MAVSDK wrapper
        │ MAVLink UDP :14540
        ▼
PX4 SITL                     ← PX4: FC (modes, EKF, tracking, mixers)
        │ gz_bridge
        ▼
Gazebo Harmonic              ← Gazebo: physics + (today) static world
```

**What ARES does today:** generate a global waypoint list and upload/execute it via high-level MAVSDK actions.  
**What ARES does not do today:** local replanning, perception, mapping from sensors, inner-loop control.

---

## 2. Ownership matrix

| Concern | ARES (this repo) | PX4 | Gazebo |
|---------|------------------|-----|--------|
| Mission intent (start/goal/RTH) | Yes (`interfaces/`, `missions/`) | No | No |
| Global path (A*) | Yes (`autonomy/`) | No | No |
| Local / dynamic planning | **Not yet** (Phase 2.2) | Partial (obstacle avoidance modes exist but we don’t use them as our stack) | No |
| Perception | **Not yet** (Phase 2.3) | Limited onboard estimators | Sensor plugins / rays |
| Mapping from sensors | **Not yet** | No (uses fused state) | Provides raw sensor truth |
| Arm / takeoff / goto / land commands | Thin API (`control/`) | Executes commands | — |
| Attitude / rate / position tracking | No | **Yes** | — |
| State estimation (EKF) | No | **Yes** | Feeds IMU/GPS via bridge |
| Motor mixing / actuator output | No | **Yes** | Applies forces |
| World geometry / collisions / physics | Static SDF copy (`simulation/`) | No | **Yes** |
| Time / sim clock | No | Syncs via bridge | **Yes** |

---

## 3. Module-by-module (current ARES code)

### 3.1 `interfaces/navigation.py` — Navigation request

| | |
|--|--|
| **Why** | Typed “what we want” without flight code |
| **Responsibility** | Parse/validate start, goal, grid, obstacles, safety, RTH flags |
| **Inputs** | JSON file / dict |
| **Outputs** | `NavigationRequest` |
| **Talks to** | Loaded by scripts / planner; **never** imports MAVSDK |
| **PX4/Gazebo?** | Neither |

### 3.2 `interfaces/mission.py` — Mission plan

| | |
|--|--|
| **Why** | Common flyable contract for Phase 1 scripts and Phase 2 planner |
| **Responsibility** | Waypoint list + timeouts / battery abort fields |
| **Inputs** | JSON or planner output |
| **Outputs** | `MissionPlan` |
| **Talks to** | Consumed by `mission_runner` |
| **PX4/Gazebo?** | Neither |

### 3.3 `autonomy/grid_map.py` — Occupancy grid

| | |
|--|--|
| **Why** | Discrete map for search |
| **Responsibility** | Build free/occupied cells; inflate obstacles |
| **Inputs** | `GridBounds`, obstacle circles, `inflation_m` |
| **Outputs** | `GridMap` |
| **Talks to** | Used only by planner |
| **PX4/Gazebo?** | Neither (map is logical; Gazebo SDF is a **separate** visual/collision twin) |

### 3.4 `autonomy/planner.py` — Global planner (A*)

| | |
|--|--|
| **Why** | Turn intent into a coarse path |
| **Responsibility** | A*, simplify, optional return path, clearance assert |
| **Inputs** | `NavigationRequest` |
| **Outputs** | `MissionPlan` |
| **Talks to** | `grid_map`, `interfaces` |
| **PX4/Gazebo?** | Neither |

### 3.5 `control/vehicle.py` — PX4 interface (thin)

| | |
|--|--|
| **Why** | Hide MAVSDK behind a small API |
| **Responsibility** | Connect, arm, takeoff, `goto_ned`, land, wait arrival |
| **Inputs** | Commands from runner; telemetry from PX4 |
| **Outputs** | MAVLink commands on UDP |
| **Talks to** | MAVSDK ↔ PX4 companion link (`14540`) |
| **PX4?** | **Yes** — receives and executes |
| **Gazebo?** | Indirect only via PX4 |

### 3.6 `control/mission_runner.py` — Mission manager (minimal)

| | |
|--|--|
| **Why** | Orchestrate one plan on one vehicle |
| **Responsibility** | Sequence waypoints; abort → emergency RTH |
| **Inputs** | `Vehicle`, `MissionPlan` |
| **Outputs** | Side effects on vehicle; `MISSION_OK` / `MISSION_ABORT_RTH` |
| **Talks to** | `vehicle` only |
| **PX4/Gazebo?** | Indirect |

### 3.7 `simulation/worlds/ares_navigate.sdf`

| | |
|--|--|
| **Why** | Visible / collidable twin of JSON obstacle |
| **Responsibility** | Gazebo world + cylinder |
| **Inputs** | Started by `start_sitl_gui.sh` |
| **Outputs** | Physics + contacts |
| **PX4?** | Spawns into this world via `gz_bridge` |
| **ARES app?** | Does **not** read this SDF at runtime for planning (duplicated knowledge today — Phase 2.3/2.4 should reduce that) |

### 3.8 Launch / demo glue

| File | Role |
|------|------|
| `scripts/start_sitl_gui.sh` | Start Gazebo world + PX4 SITL |
| `scripts/run_planned_mission.py` | Plan + fly entry |
| `run_ares_demo.py` / `.bat` | Windows one-click orchestration |

---

## 4. PX4 responsibilities (what you rely on)

When ARES calls `goto_ned` / `takeoff` / `land`:

1. MAVLink command accepted by PX4 `mavlink` → `commander`
2. Mode / setpoint generated (e.g. position control)
3. Multicopters: position → attitude → rate → allocator → motor commands
4. `gz_bridge` publishes motor speeds to Gazebo; subscribes IMU/GPS/…
5. `ekf2` fuses sensors → position used for tracking

ARES does **not** replace this loop in Phase 2A.

---

## 5. Gazebo responsibilities

1. Integrate rigid-body dynamics  
2. Resolve collisions (e.g. cylinder)  
3. Run sensor plugins (when we add them in 2.3)  
4. Provide the plant that PX4 “thinks” is the airframe  

---

## 6. Target architecture (Phase 2B)

```
┌─────────────────┐
│ Mission Manager │  (evolve mission_runner)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Global Planner  │  (keep A*)
└────────┬────────┘
         ▼ reference path
┌─────────────────┐     ┌────────────┐
│ Local Planner   │◄────│  Mapping   │
└────────┬────────┘     └─────▲──────┘
         │                    │
         ▼                    │
┌─────────────────┐     ┌─────┴──────┐
│ Controller I/F  │     │ Perception │
└────────┬────────┘     └─────▲──────┘
         ▼                    │
┌─────────────────┐           │
│ PX4 Interface   │     (Gazebo sensors)
└────────┬────────┘
         ▼
       PX4 SITL  ←→  Gazebo
```

Scaling to Phase 3: one **PX4 Interface + autonomy stack instance per vehicle**; `swarm/` only assigns missions.

---

## 7. ROS 2 readiness (preview for Phase 2.5)

| Module | Likely ROS 2 node? | Why |
|--------|--------------------|-----|
| Perception | **Yes** | Natural pub/sub for sensors (`ros_gz`) |
| Mapping | **Yes** | Consumes perception, publishes costmap |
| Local Planner | **Yes** | Timer-driven; needs live map + odom |
| Global Planner | Maybe | Often on-demand service, not a forever spin |
| Mission Manager | Maybe | Service/action; can stay Python app early |
| PX4 Interface | Optional | MAVSDK OK; `px4_ros_com` / MAVROS later if needed |
| Controller I/F | Maybe | If setpoints are topics |

Do **not** migrate until perception/local planner need the bus.

---

## 8. How to debug today’s stack

1. **Plan only:** `python scripts/run_planned_mission.py missions/navigate_demo.json --plan-only`  
2. **Clearance:** `python scripts/check_plan_avoidance.py`  
3. **Unit tests:** `python -m unittest tests.test_planner tests.test_mission`  
4. **Flight:** `run_ares_demo.bat` → look for `MISSION_OK`  
5. **Sim log:** `_ares_demo_sitl.log` for PX4/Gazebo bring-up  
6. **Separation test:** If plan is good but flight hits obstacle → tracking/safety margin/PX4 corner-cutting — not A* “wrong topology”

---

## 9. Phase 2.1 checklist (for you)

After reading this doc, you should be able to answer:

1. What does ARES compute vs what PX4 tracks?  
2. Why can the drone hit a cylinder even if A* is “SAFE”?  
3. Why JSON obstacles and Gazebo SDF can drift apart?  
4. What new boxes are empty today (local planner, perception, mapping)?  

When those answers are clear, start Phase 2.2 **design** (still before large code dumps).
