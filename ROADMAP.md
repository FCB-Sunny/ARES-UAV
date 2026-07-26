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

## Phase 1 — Foundation Flight (Week 1–2) ✅

**Goal:** One drone flies autonomously in simulation.

- [x] Repo modules: `interfaces/` (mission data) + `control/` (MAVSDK vehicle)
- [x] Scripted mission: arm → takeoff → waypoints → land (`missions/square_demo.json`)
- [x] Verify on host via `run_ares_demo.bat`
- [ ] Record demo video / log (optional)

**Exit:** Reproducible single-vehicle waypoint flight. — **met**

---

## Phase 2 — Autonomous Navigation (Week 3–4) ← in progress

**Goal:** Navigate with obstacles.

- [x] Path planning skeleton: A* in `autonomy/` → `MissionPlan`
- [x] Navigation request schema (`interfaces/navigation.py`) + `missions/navigate_demo.json`
- [x] Gazebo world obstacle aligned with JSON (`simulation/worlds/ares_navigate.sdf`)
- [x] Safety-radius inflation (clearance for vehicle / tracking)
- [x] Return-to-home path + timeout/battery abort in `control/mission_runner.py`
- [ ] Verify full out-and-back flight on SITL (`run_ares_demo.bat`)

**Exit:** Start → avoid → goal → home.

---

## Phase 3 — Multi-Drone System (Month 2)

**Goal:** 3–5 drones cooperate.

- Multi-SITL bring-up (resource-aware on 16 GB host)
- Communication + simple task allocation
- Formation or sector search demo

**Exit:** Swarm search mission demo.

---

## Phase 4 — AI Mission Commander (Month 3)

**Goal:** Natural language → executed mission.

- LLM API integration (cloud first)
- Mission schema validation
- Planner bridge from JSON → vehicle tasks

**Exit:** “Find survivors in this area” style command runs end-to-end in sim.

---

## Phase 5 — Advanced Research (Month 4+)

**Goal:** Research features after core stack is stable.

- GPS-denied / VIO / SLAM experiments
- RL navigation (cloud GPU later)
- Digital twin concepts

Only begin when Phases 0–3 are reliable.

---

## Tracking Rule

Check items only after verification on this host. Do not mark future phases complete early.
