# ARES-UAV

**Autonomous Robotic Environment & Swarm Intelligence System**

ARES-UAV is an autonomous UAV swarm simulation platform. Multiple drones receive high-level missions from an AI commander, plan tasks, navigate safely, and cooperate — without continuous human control.

> **Status:** Phase 0 — Engineering foundation (environment + documentation). No autonomy code yet.

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

## System Layers

| Layer | Purpose | Stack (v1) |
|-------|---------|------------|
| Simulation | Physics, sensors, world | Gazebo Harmonic, PX4 SITL |
| Flight control | Arm, takeoff, waypoints, offboard | MAVSDK Python, MAVLink |
| Autonomy | Planning, localization, control | Python (ROS 2 Humble) |
| Swarm | Formation, allocation, avoidance | Consensus → MARL later |
| Perception | Detect / track / obstacles | OpenCV, YOLOv8 (CPU) |
| AI commander | NL → mission JSON | Cloud LLM API first |

## Host Constraints

- Windows 10 + **WSL2 Ubuntu 22.04**
- No local GPU training / Isaac Sim in v1
- Start with **one** simulated drone, then scale

## Repository Layout (target)

```
ARES-UAV/
├── README.md
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── DEVELOPMENT_RULES.md
├── ENVIRONMENT_SETUP.md
├── docs/
├── simulation/
├── autonomy/
├── swarm/
├── perception/
├── ai_agent/
├── control/
├── interfaces/
├── tests/
└── tools/
```

## Documentation

| Document | Contents |
|----------|----------|
| [PROJECT_SPEC.md](PROJECT_SPEC.md) | Mission, scope, requirements |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layers, data flow, interfaces |
| [ROADMAP.md](ROADMAP.md) | Phased milestones |
| [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) | Engineering standards |
| [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) | WSL / ROS 2 / PX4 / Gazebo / MAVSDK plan |

## Quick Start (after Phase 0 install)

1. Read `ENVIRONMENT_SETUP.md` and complete verification checklist.
2. Confirm: ROS 2 → Gazebo → PX4 SITL → MAVSDK takeoff/land.
3. Follow `ROADMAP.md` Phase 1 — do not skip foundation checks.

## License

TBD — will be declared before public release of application code.
