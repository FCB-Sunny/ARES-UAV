# ARES-UAV

**Autonomous Robotic Environment & Swarm Intelligence System**

ARES-UAV is an autonomous UAV swarm simulation platform. Multiple drones receive high-level missions from an AI commander, plan tasks, navigate safely, and cooperate — without continuous human control.

> **Status:** Phase 2A complete (mission + global A*). **Phase 2B** next — single-UAV autonomy (local planner, perception). Phase 3 waits.

---

## Vision

```
Human Operator
      │  Natural language mission
      ▼
LLM Mission Commander
      │  Structured mission plan
      ▼
Mission Planning / Task Allocation
      │
 ┌────┼────┐
Drone 1 … Drone N
      │
Autonomous Navigation
      │
PX4 Flight Controller (SITL)
      │
Gazebo Simulation
```

## What lives where

| Location | What it is | Do you edit it? |
|----------|------------|-----------------|
| This GitHub repo | Specs + future ARES app code + demo scripts | **Yes** (your project) |
| WSL Ubuntu (`~/PX4-Autopilot`, ROS, Gazebo) | Installed simulator / autopilot tools | **No** (use them, don’t study every file) |
| `control/`, `autonomy/`, `interfaces/`, … | ARES app (mission + planners) | **Yes** |
| Living architecture review | [`docs/PHASE2_ARCHITECTURE.md`](docs/PHASE2_ARCHITECTURE.md) | Read first for Phase 2B |

## Phase 1 demo (one command)

Prerequisites: WSL2 Ubuntu 22.04, ROS 2 Humble, Gazebo Harmonic, PX4 SITL, `~/ares-venv` with MAVSDK, VcXsrv on Windows.

From Windows:

```bat
run_ares_demo.bat
```

Or:

```powershell
cd C:\Users\a\Projects\ARES-UAV
python run_ares_demo.py
```

Starts Gazebo + PX4, then plans + flies `missions/navigate_demo.json` (A* around a JSON obstacle).

**Where to read code (software layers):**

| Layer | Path | What you learn |
|-------|------|----------------|
| Navigate intent | [`interfaces/navigation.py`](interfaces/navigation.py) | Start/goal/obstacles (Phase 2) |
| Planner | [`autonomy/planner.py`](autonomy/planner.py) | A* → `MissionPlan` |
| Mission data | [`interfaces/mission.py`](interfaces/mission.py), [`missions/`](missions/) | Flyable waypoints |
| Flight API | [`control/vehicle.py`](control/vehicle.py) | Only place that imports MAVSDK |
| Orchestration | [`control/mission_runner.py`](control/mission_runner.py) | Mission steps in order |
| Entry | [`scripts/run_waypoint_mission.py`](scripts/run_waypoint_mission.py) / [`run_planned_mission.py`](scripts/run_planned_mission.py) | CLI glue |
| Sim bring-up | [`scripts/start_sitl_gui.sh`](scripts/start_sitl_gui.sh) | Gazebo + PX4 (treat as tool) |

Unit tests (no sim):

```bat
python -m unittest tests.test_mission tests.test_planner
```

Plan only (no sim):

```bat
python scripts/run_planned_mission.py missions/navigate_demo.json --plan-only
```

## Repository layout

```
ARES-UAV/
├── run_ares_demo.bat / .py   ← one-click demo
├── missions/                 ← waypoint + navigation JSON demos
├── interfaces/               ← mission + navigation schemas
├── control/                  ← MAVSDK vehicle + mission runner
├── autonomy/                 ← Phase 2 A* planner
├── simulation/               ← Gazebo worlds (obstacle demo)
├── scripts/                  ← launch + CLI entry
├── tests/
├── swarm/ perception/ …      ← later phases
└── docs/
```

## Documentation

| Document | Contents |
|----------|----------|
| [PROJECT_SPEC.md](PROJECT_SPEC.md) | Mission, scope, requirements |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layers, data flow, interfaces |
| [ROADMAP.md](ROADMAP.md) | Phased milestones |
| [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) | Engineering standards |
| [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) | WSL / ROS 2 / PX4 / Gazebo / MAVSDK setup |

## License

TBD — will be declared before public release of application code.
