# ARES-UAV — Architecture

## 1. Host / Runtime Topology

```
Windows 10
    │
    ▼
WSL2 (Ubuntu 22.04 LTS)
    │
    ├── ROS 2 Humble
    ├── Gazebo Harmonic (+ ros_gz)
    ├── PX4 Autopilot SITL
    ├── MAVSDK Python / pymavlink
    └── ARES application packages (future)
```

All robotics processes run **inside WSL2**. Prefer keeping MAVSDK clients in the same WSL instance as PX4 to avoid UDP port-forward complexity.

## 2. Logical Layers

```
┌─────────────────────────────────────────────┐
│  L6  AI Mission Commander (LLM)             │
│      NL → validated mission JSON            │
├─────────────────────────────────────────────┤
│  L5  Perception                             │
│      detection / tracking / landing zones   │
├─────────────────────────────────────────────┤
│  L4  Swarm Intelligence                     │
│      allocation / formation / avoidance     │
├─────────────────────────────────────────────┤
│  L3  Autonomy Stack                         │
│      Mission → Planner → Path → Controller  │
├─────────────────────────────────────────────┤
│  L2  Flight Control Interface               │
│      MAVSDK / offboard / telemetry          │
├─────────────────────────────────────────────┤
│  L1  Simulation                             │
│      Gazebo ↔ PX4 SITL ↔ sensors            │
└─────────────────────────────────────────────┘
```

## 3. Autonomy Internal Pipeline

```
Mission
  → Planner (global)
  → Path Generator (A* / RRT* / …)
  → Trajectory Controller (PID → LQR/MPC later)
  → PX4 offboard setpoints
```

## 4. Interface Contracts (initial)

### Mission JSON (AI commander → planner)

```json
{
  "mission": "search",
  "drones": 5,
  "area": "sector_A",
  "battery_limit": 20
}
```

Schema will be versioned under `interfaces/` once implementation starts.

### Flight API (planner → vehicle)

- `connect(system_address)`
- `arm()` / `disarm()`
- `takeoff()` / `land()`
- `goto(lat, lon, alt)` / velocity offboard

Primary library: **MAVSDK Python**.

### ROS 2

- Use ROS 2 for perception streams, swarm messaging, and tooling.
- Keep a clear boundary: ROS topics are not a substitute for a typed mission schema.

## 5. Package Boundaries (future code)

| Package | Responsibility |
|---------|----------------|
| `simulation/` | Launch files, worlds, model configs |
| `control/` | MAVSDK wrappers, offboard helpers |
| `autonomy/` | Planning, localization, control laws |
| `swarm/` | Multi-agent coordination |
| `perception/` | Vision pipelines |
| `ai_agent/` | LLM client + mission validation |
| `interfaces/` | Shared schemas / message defs |
| `tests/` | Integration and unit tests |
| `tools/` | Dev scripts, diagnostics |

## 6. Design Principles

1. Spec and architecture before features  
2. One drone proven before swarm  
3. Headless simulation preferred on this host  
4. No unnecessary dependencies  
5. Fail closed on invalid mission JSON  
