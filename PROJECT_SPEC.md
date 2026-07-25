# ARES-UAV — Project Specification

**Codename:** ARES (Autonomous Robotic Environment & Swarm Intelligence System)  
**Short name:** ARES-UAV  
**Owner:** FCB-Sunny  
**Document role:** Primary source of truth for scope and intent  

---

## 1. Mission

Build a complete **autonomous UAV swarm simulation platform** where multiple drones can:

1. Receive high-level missions from an AI agent (natural language → structured plan)
2. Plan and allocate tasks autonomously
3. Navigate safely in simulation
4. Cooperate as a swarm without continuous human teleoperation

## 2. Goals

### Primary (portfolio / research demo)

- One drone: arm → takeoff → waypoint → land via MAVSDK
- Obstacle-aware navigation in Gazebo
- Multi-drone search / allocation demo
- LLM mission commander producing executable mission JSON

### Non-goals (v1)

- Real hardware flight certification
- Isaac Sim
- Local large-model training / fine-tuning
- Production cloud fleet ops

## 3. System Overview — Six Layers

1. **Simulation** — Gazebo Harmonic + PX4 SITL + ROS 2 Humble  
2. **Flight control** — MAVSDK / MAVLink offboard interface  
3. **Autonomy** — planners, localization, controllers  
4. **Swarm** — allocation, formation, collision avoidance  
5. **Perception** — OpenCV / YOLO (CPU first)  
6. **AI Mission Commander** — LLM → mission schema → planner  

## 4. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Simulate at least one PX4 multirotor in Gazebo | P0 |
| FR-02 | Control drone via MAVSDK Python (arm/takeoff/goto/land) | P0 |
| FR-03 | ROS 2 nodes publish/subscribe mission and telemetry topics | P1 |
| FR-04 | Path planning with obstacle avoidance | P1 |
| FR-05 | Support 3–5 SITL instances with task allocation | P2 |
| FR-06 | NL mission → validated JSON mission plan | P2 |
| FR-07 | Object detection pipeline (CPU) on camera stream | P2 |

## 5. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Runs on Windows 10 host via WSL2 Ubuntu 22.04 |
| NFR-02 | Works without dedicated ML GPU for core demos |
| NFR-03 | Every module ships with README, unit test, example usage |
| NFR-04 | Prefer Python; C++ only when performance requires it |
| NFR-05 | Reproducible pinned versions documented after install |

## 6. Success Criteria (Phase gates)

- **Phase 0:** ROS 2 + Gazebo + PX4 SITL + MAVSDK takeoff/land verified  
- **Phase 1:** Recorded demo of single autonomous waypoint mission  
- **Phase 2:** Obstacle avoidance + return-to-home  
- **Phase 3:** Multi-drone coordinated search  
- **Phase 4:** LLM commander drives a real mission plan end-to-end  

## 7. Out of Scope Notes

Do not expand scope into hardware bring-up, CUDA training, or Isaac Sim until Phase 0–2 are stable on this host.
