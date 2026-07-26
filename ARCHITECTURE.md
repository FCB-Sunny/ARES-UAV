# ARES-UAV — Architecture

## 1. Host / Runtime Topology

```
Windows 10
    │
    ▼
WSL2 (Ubuntu 22.04 LTS)
    │
    ├── ROS 2 Humble          (installed; used lightly until Phase 2.5+)
    ├── Gazebo Harmonic
    ├── PX4 Autopilot SITL
    ├── MAVSDK Python
    └── ARES application (this repo)
```

All robotics processes run **inside WSL2**. Keep MAVSDK clients in the same WSL instance as PX4.

---

## 2. Ownership (critical)

| Layer | Owner |
|-------|--------|
| Mission intent, global/local planning, perception, mapping (ARES) | **This repo** |
| Stabilization, EKF, mode machine, trajectory tracking | **PX4** |
| Physics, collisions, sensor simulation | **Gazebo** |

Phase 2A only implemented the **mission + global path** slice of ARES. Phase 2B adds local planning and perception. See [`docs/PHASE2_ARCHITECTURE.md`](docs/PHASE2_ARCHITECTURE.md).

---

## 3. Logical Layers

```
┌─────────────────────────────────────────────┐
│  L6  AI Mission Commander (LLM) — Phase 4   │
├─────────────────────────────────────────────┤
│  L5  Perception + Mapping — Phase 2.3       │
├─────────────────────────────────────────────┤
│  L4  Swarm Intelligence — Phase 3           │
├─────────────────────────────────────────────┤
│  L3  Autonomy                               │
│      Mission Manager → Global → Local       │
│      → Controller Interface                 │
├─────────────────────────────────────────────┤
│  L2  PX4 Interface (MAVSDK / offboard)      │
├─────────────────────────────────────────────┤
│  L1  Simulation (Gazebo ↔ PX4 SITL)         │
└─────────────────────────────────────────────┘
```

---

## 4. Target autonomy pipeline (Phase 2B)

```
Mission
  → Global Planner (A*)
  → Local Planner (online / dynamic)
  → Controller Interface (setpoints)
  → PX4 Interface
  → PX4  ↔  Gazebo
         ↑
Perception → Mapping
```

**Current (Phase 2A) pipeline** skips Local Planner, Perception, and Mapping:

```
Mission → Global A* → MAVSDK goto list → PX4 → Gazebo
```

---

## 5. Interface contracts

### Navigation / mission (ARES-owned)

Versioned under `interfaces/` (`NavigationRequest`, `MissionPlan`, …).  
Fail closed on invalid JSON.

### Flight API (ARES → PX4)

- `connect` / `arm` / `takeoff` / `land` / `goto` (today)
- Offboard velocity/position setpoints (Phase 2.2+)

Primary library today: **MAVSDK Python**.

### ROS 2

- Preferred later for perception streams and multi-node autonomy (Phase 2.5 design).
- Do not migrate solely for fashion; require a clear pub/sub benefit.

---

## 6. Package boundaries

| Package | Responsibility |
|---------|----------------|
| `interfaces/` | Typed contracts (no MAVSDK) |
| `autonomy/` | Global (+ later local) planning |
| `control/` | Mission runner + PX4/MAVSDK interface |
| `perception/` | Sensor consumers / detectors (Phase 2.3) |
| `simulation/` | ARES-owned worlds / models |
| `swarm/` | Multi-vehicle coordination (Phase 3) |
| `ai_agent/` | LLM commander (Phase 4) |
| `tests/` | Unit / integration tests |
| `docs/` | Architecture reviews, designs |

Target single-responsibility names (Phase 2.4): Mission Manager, Global Planner, Local Planner, Perception, Mapping, Controller Interface, PX4 Interface.

---

## 7. Design principles

1. Spec and architecture **before** features (Phase 2.6)  
2. One drone autonomy mature before swarm  
3. Separate ARES / PX4 / Gazebo responsibilities in docs and code  
4. Prefer headless Gazebo during heavy iteration on this host  
5. Fail closed on invalid mission / map data  
6. ROS 2 only where it clearly helps  
