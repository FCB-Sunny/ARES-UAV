# ARES-UAV

**Autonomous Robotic Environment & Swarm Intelligence System**

ARES-UAV is an autonomous UAV swarm simulation platform. Multiple drones receive high-level missions from an AI commander, plan tasks, navigate safely, and cooperate — without continuous human control.

> **Status:** Phase 0 complete (environment verified). Phase 1 next — scripted waypoint flight.

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
| Empty folders (`control/`, `autonomy/`, …) | Placeholders for Phase 1+ | Fill later |

## Phase 0 demo (one command)

Prerequisites (already set up on the ARES host): WSL2 Ubuntu 22.04, ROS 2 Humble, Gazebo Harmonic, PX4 SITL build, `~/ares-venv` with MAVSDK, VcXsrv on Windows.

From Windows:

```bat
run_ares_demo.bat
```

Or:

```powershell
cd C:\Users\a\Projects\ARES-UAV
python run_ares_demo.py
```

That starts Gazebo (3D window) + PX4, then runs arm → takeoff → land.

Readable demo code:

- [`scripts/mavsdk_takeoff_land.py`](scripts/mavsdk_takeoff_land.py)
- [`scripts/start_sitl_gui.sh`](scripts/start_sitl_gui.sh)
- [`scripts/README.md`](scripts/README.md)

## Repository layout

```
ARES-UAV/
├── README.md
├── PROJECT_SPEC.md / ARCHITECTURE.md / ROADMAP.md / ...
├── run_ares_demo.bat      ← one-click Windows launcher
├── run_ares_demo.py
├── scripts/               ← Phase 0 demo scripts (read these)
├── control/ autonomy/ …   ← empty until Phase 1+
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
