# Phase 2.2 — Local Planner Design Guide

**Audience:** you implement; mentor reviews architecture first.  
**Prerequisite:** Phase 2.1 — [`PHASE2_ARCHITECTURE.md`](PHASE2_ARCHITECTURE.md)  
**Rule:** Do **not** delete or replace global A*. Local planner sits **between** global path and PX4.

---

## 1. Goal

Today:

```
Global A* → list of gotos → PX4
```

Target:

```
Global A* → reference path
                ↓
         Local Planner (online, ~10–50 Hz later; start slower)
                ↓
         setpoints → PX4 Interface
```

Local planner must **react to map changes** (Phase 2.3 will feed the map). For 2.2 you may still inject a *fake* moving obstacle into the local costmap to prove the loop.

---

## 2. What local planning is (and is not)

| Local planner **is** | Local planner **is not** |
|----------------------|---------------------------|
| Short horizon (e.g. 2–10 s or 5–20 m) | Full map A* every cycle |
| Uses robot pose + local obstacles | Inner-loop attitude control (PX4) |
| Outputs velocity or position setpoints | Replacing EKF |

---

## 3. Recommended first algorithm (for learning + SITL)

### Choice: **DWA-lite / dynamic window** (velocity sampling)

**Why for ARES now**

- Easy to understand and debug  
- Fits “continuous update during flight”  
- Works with a 2D local costmap  
- Natural next step before TEB / MPC  

**References (read in order)**

1. Fox, Burgard, Thrun — *The Dynamic Window Approach to Collision Avoidance* (classic DWA paper)  
2. ROS Navigation: [DWA local planner overview](http://wiki.ros.org/dwa_local_planner) (concepts; you need not use ROS yet)  
3. PX4 Offboard: [MAVSDK Offboard](https://mavsdk.mavlink.io/main/en/python/api_reference/classmavsdk_1_1offboard_1_1_offboard.html) — velocity/position setpoint streaming  

**Alternative (later):** TEB, MPPI, simple “VFH+”, or pure pursuit + reactive sidestep. Do **not** start with MPC.

---

## 4. Target module layout (you create)

Suggested paths (aligns with Phase 2.4 names):

```
autonomy/
  planner.py              # KEEP — global A* only
  local_planner.py        # NEW — online local
  local_costmap.py        # NEW — rolling window grid (can start stub)
control/
  vehicle.py              # EXTEND later — offboard setpoint API
  mission_runner.py       # OR thin mission_manager — call local loop
interfaces/
  local_plan.py           # NEW — LocalPlan / Twist2D / Pose2D types
```

**Dependency rule:** `local_planner` must **not** import MAVSDK. It outputs setpoints; `control/vehicle.py` sends them.

---

## 5. Interfaces to design first (before coding)

Sketch these dataclasses (names flexible):

```text
Pose2D(north_m, east_m, yaw_rad)
Twist2D(vn_m_s, ve_m_s, yaw_rate_rad_s)   # or body-frame vx,vy

LocalCostmap
  - resolution_m, width_m, height_m
  - robot-centered or world-fixed window
  - occupied / cost cells

LocalPlannerInput
  - pose: Pose2D
  - velocity: Twist2D (optional)
  - global_path: list[Pose2D] or remaining waypoints
  - costmap: LocalCostmap

LocalPlannerOutput
  - cmd: Twist2D  (preferred for “continuous”)
  - OR next_position: Pose2D
  - status: OK | BLOCKED | GOAL_REACHED
```

Write the types in `interfaces/` **before** the algorithm body.

---

## 6. Data flow (execution story)

```
1. Mission Manager loads NavigationRequest
2. Global planner → MissionPlan / polyline path
3. Vehicle arms, takes off (unchanged)
4. LOOP (e.g. 5–10 Hz to start):
     a. read pose from PX4 telemetry (via vehicle)
     b. update local costmap (stub: static + injected obstacle)
     c. local_planner.step(input) → Twist2D
     d. vehicle.set_velocity_ned(twist)   # offboard
     e. if near final goal → break → land / RTH policy
5. On BLOCKED too long → abort RTH (reuse existing abort idea)
```

**Important PX4 note:** streaming setpoints usually needs **Offboard mode** + a setpoint heartbeat (MAVSDK Offboard `start` + periodic `set_velocity_ned`). Plain `action.goto_location` is **not** a local planner loop.

---

## 7. Minimal DWA-lite algorithm (pseudocode)

```text
samples = combinations of (v_forward, yaw_rate) inside dynamic window
for each sample:
  simulate short trajectory (0.5–2.0 s) with simple unicycle / holonomic model
  if trajectory hits costmap → discard
  else score = w_goal * progress_along_global_path
             + w_clear * distance_to_obstacle
             + w_path * distance_to_global_path
             - w_speed * |v - v_desired|
pick best sample → send as velocity command
```

Start **holonomic / NED velocity** (multicopter): sample `(vn, ve)` in a disk of max speed — simpler than differential-drive DWA.

---

## 8. Implementation milestones (your checklist)

### M0 — Types only
- [ ] `interfaces/local_plan.py` (+ unit tests for validation)

### M1 — Costmap stub
- [ ] Robot-centered grid; stamp circles; query collision for a polyline

### M2 — Local planner offline
- [ ] `step()` with fake pose + fake costmap; **no PX4**
- [ ] Unit test: path around a blocking cell in front of the robot

### M3 — Vehicle offboard API
- [ ] `vehicle.py`: `start_offboard`, `set_velocity_ned`, `stop_offboard`
- [ ] Tiny script: hover / move 2 m with offboard (SITL)

### M4 — Integrate loop
- [ ] Mission: global plan → local loop follows path
- [ ] Inject moving obstacle in costmap mid-flight → see detour

### M5 — Docs
- [ ] `autonomy/README.md` section for local planner
- [ ] How to debug (below)

Do not jump to M4 before M2 works.

---

## 9. How to debug

| Symptom | Check |
|---------|--------|
| Drone ignores local commands | Offboard started? Setpoint rate > ~2 Hz? PX4 still in Offboard? |
| Oscillation | Lower rate; smooth scores; limit accel |
| Always blocked | Costmap inflation too large; robot pose frame wrong (NED vs ENU) |
| Cuts through obstacle | Collision check uses robot radius; sample resolution |
| Diverges from goal | Increase `w_goal` / path progress term |

**Offline first:** print chosen `(vn, ve)` and ASCII costmap each step — same idea as `check_plan_avoidance.py`.

---

## 10. Frames (do not skip)

| Frame | Use |
|-------|-----|
| ARES planner / costmap | Local **N/E** meters from home (as today) |
| Gazebo world | **ENU** (x=east, y=north) |
| PX4 local | Often **NED** for velocity setpoints |

Document every conversion in code comments once. Most “local planner bugs” are frame bugs.

---

## 11. What to send the mentor when stuck

1. Which milestone (M0–M5)  
2. Interface sketch or file paths you added  
3. Expected vs actual (one short log)  
4. Question: architecture / algorithm / PX4 — not “write it all for me”  

When you want a code review or a specific function filled in, **ask explicitly**.

---

## 12. Suggested first coding task (today)

1. Create `interfaces/local_plan.py` with `Pose2D`, `Twist2D`, `LocalPlannerOutput`  
2. Add `tests/test_local_plan_types.py`  
3. Paste your interface here for review before writing DWA  

No PX4 required for that step.
