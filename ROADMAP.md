# ARES-UAV — Development Roadmap

## Phase 0 — Environment & Foundation ✅

**Goal:** Reproducible engineering baseline.

- [x] Host analysis + `ENVIRONMENT_SETUP.md`
- [x] WSL2 + Ubuntu 22.04 operational
- [x] GitHub repository created
- [x] ROS 2 Humble installed and verified
- [x] Gazebo Harmonic launches
- [x] PX4 SITL `gz_x500` runs
- [x] MAVSDK arm / takeoff / land demo
- [ ] WSL snapshot backup after success (optional)

**Exit:** Single simulated UAV controllable via MAVSDK. — **met** (`run_ares_demo.bat`)

---

## Phase 1 — Foundation Flight ✅

**Goal:** One drone flies a scripted waypoint mission in simulation.

- [x] Repo modules: `interfaces/` (mission data) + `control/` (MAVSDK vehicle)
- [x] Scripted mission: arm → takeoff → waypoints → land (`missions/square_demo.json`)
- [x] Verify on host via `run_ares_demo.bat`
- [ ] Record demo video / log (optional)

**Exit:** Reproducible single-vehicle waypoint flight. — **met**

---

## Phase 2A — Mission Planning Baseline ✅

**Honest scope note:** This phase built a **mission / global-path planning system**, not a full autonomy stack.

```
Mission JSON → Global Planner (A*) → Waypoint sequence → MAVSDK → PX4 → Gazebo
```

ARES owns: mission schema, A*, safety inflation, RTH path append, thin MAVSDK runner.  
PX4 owns: stabilization, tracking, mode logic, EKF.  
Gazebo owns: physics, sensors, world geometry.

- [x] A* global planner → `MissionPlan`
- [x] Navigation request schema + `missions/navigate_demo.json`
- [x] Gazebo cylinder world aligned with JSON map
- [x] Safety-radius inflation
- [x] Return-to-home path + timeout/battery abort
- [x] Verified out-and-back SITL demo

**Exit:** Start → avoid (known map) → goal → home. — **met**

---

## Phase 2B — Single-UAV Autonomy Stack ← current

**Goal:** Strengthen **one** UAV’s autonomy before multi-drone.  
**Rule:** Architecture and understanding first; implementation second.  
**Gate:** Do **not** start Phase 3 until 2B exit is met.

Target pipeline:

```
Mission Manager
  → Global Planner (A* / known or mapped free space)
  → Local Planner (online trajectory / dynamic avoid)
  → Controller Interface (setpoints)
  → PX4 Interface (MAVSDK / offboard)
  → PX4 + Gazebo
       ↑
Perception → Mapping (local occupancy / costmap)
```

### Phase 2.1 — Architecture Review

- [x] Document ownership: ARES vs PX4 vs Gazebo for every module in the current pipeline
- [x] Inputs / outputs / communication for each ARES package
- [x] Living doc: [`docs/PHASE2_ARCHITECTURE.md`](docs/PHASE2_ARCHITECTURE.md)

**Exit:** You can explain the pipeline without treating PX4/Gazebo as mystery boxes. — **met** (owner ready for 2.2)

### Phase 2.2 — Dynamic Local Planning

- [ ] Keep A* as **global** planner only
- [ ] Design local planner (architecture + algorithm choice) before coding — guide: [`docs/PHASE2_2_LOCAL_PLANNER_DESIGN.md`](docs/PHASE2_2_LOCAL_PLANNER_DESIGN.md)
- [ ] Implement online local trajectory / dynamic obstacle reaction (owner-led)
- [ ] Wire: Global path → Local planner → PX4 setpoints (prefer offboard over open-loop goto list)

**Exit:** Vehicle reacts to a **moving / newly appearing** obstacle without a full global replan-only workflow.

### Phase 2.3 — Perception Integration

- [ ] Add simulated sensor(s) in Gazebo (LiDAR and/or depth/RGB as feasible)
- [ ] Perception module publishes detections or range data into ARES
- [ ] Mapping updates a local costmap / obstacle set from perception
- [ ] Local planner consumes the live map (not only static JSON)

**Exit:** At least one obstacle is discovered from sensors and avoided online.

### Phase 2.4 — Software Architecture (modularize)

Organize for reuse and later multi-UAV (clear interfaces, single responsibility):

| Module | Responsibility |
|--------|----------------|
| Mission Manager | Load / validate / sequence missions |
| Global Planner | Coarse path in known/mapped space |
| Local Planner | Short-horizon trajectory / avoid |
| Perception | Sensor → detections / features |
| Mapping | Occupancy / costmap maintenance |
| Controller Interface | Trajectory → setpoints |
| PX4 Interface | MAVSDK / MAVLink to one vehicle |

- [ ] Split packages/interfaces to match the table (incremental refactors OK)
- [ ] No new “god script”; demos only orchestrate modules
- [ ] Each module: README + tests + typed boundaries in `interfaces/`

**Exit:** A second vehicle *could* be added by instantiating interfaces — even if we still run one.

### Phase 2.5 — Prepare for ROS 2 (design only)

- [ ] For each module: should it become a ROS 2 node? Why / why not?
- [ ] Document topic/service candidates (no mandatory migration yet)
- [ ] Introduce ROS 2 **only** where it clearly helps (e.g. sensor bridges)

**Exit:** Written ROS 2 migration map; code may remain MAVSDK-direct until justified.

### Phase 2.6 — Working agreement (ongoing)

When adding or changing autonomy features:

1. Architecture impact  
2. Algorithm  
3. Data flow  
4. Why this design  
5. Exact files + execution path  
6. How to debug  
7. **Then** implement  

**Exit:** Continuous — enforced for all 2B work.

**Phase 2B exit (overall):** Single UAV with global + local planning + perception-driven map updates, modular interfaces, and a ROS 2 plan — verified in SITL.

---

## Phase 3 — Multi-Drone System (after Phase 2B)

**Goal:** 3–5 drones cooperate on the **same autonomy architecture**.

- Multi-SITL bring-up (resource-aware on 16 GB host)
- Per-vehicle instances of Mission / Global / Local / PX4 Interface
- Communication + simple task allocation in `swarm/`
- Formation or sector search demo

**Exit:** Swarm search mission demo.

---

## Phase 4 — AI Mission Commander

**Goal:** Natural language → executed mission.

- LLM API integration (cloud first)
- Mission schema validation
- Planner bridge from JSON → vehicle tasks

**Exit:** “Find survivors in this area” style command runs end-to-end in sim.

---

## Phase 5 — Advanced Research

**Goal:** Research features after core stack is stable.

- GPS-denied / VIO / SLAM experiments
- RL navigation (cloud GPU later)
- Digital twin concepts

Only begin when Phases 0–2B (and preferably 3) are reliable.

---

## Tracking Rule

Check items only after verification on this host. Do not mark future phases complete early.  
Phase 3 must not start until Phase 2B exit is met.
