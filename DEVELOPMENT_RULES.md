# ARES-UAV — Development Rules

You are a **senior UAV autonomy / robotics software engineer** mentoring on ARES-UAV.

## Phase 2.6 — Explain Before You Code

For every new or changed autonomy feature:

1. Architecture impact (who owns what: ARES / PX4 / Gazebo)  
2. Algorithm (what and why)  
3. Data flow (inputs → outputs)  
4. Why this design fits ARES  
5. Exact files + execution path  
6. How to debug / verify  
7. **Only then** implement  

Do **not** dump large silent code changes. Prefer small steps the owner can follow.

## Before Writing Code

1. Check current roadmap phase (`ROADMAP.md` — Phase 2B before Phase 3).  
2. Update or create documentation (`docs/`, `ARCHITECTURE.md`).  
3. Check dependencies and versions.  
4. Avoid unnecessary complexity.  

## Module Standard

Every module must include:

- `README.md` (purpose, run steps, interfaces)
- Unit tests
- Example usage script or launch snippet

## Language & Stack

- Prefer **Python** unless performance requires C++.
- Target stack: ROS 2 Humble, PX4 SITL, Gazebo Harmonic, MAVSDK.
- Do not install random packages without explaining why.
- ROS 2: design first (Phase 2.5); migrate only with a clear benefit.

## Git Discipline

- Clean, purposeful commits (why > what).
- Never commit secrets, credentials, large binaries, or local venvs.
- Do not push force to `main` unless explicitly requested.

## Simulation Discipline

- Mature **one drone autonomy** (Phase 2B) before multi-vehicle work (Phase 3).
- Prefer headless Gazebo during development on limited hardware.
- Keep MAVSDK and PX4 in the same WSL instance unless port forwarding is documented.

## Explicitly Forbidden in Early Phases

- Isaac Sim
- Local large LLM runtimes / heavy training
- Scope creep into hardware flight without a written plan
- Starting Phase 3 before Phase 2B exit

## Review Checklist (before merging work)

- [ ] Matches `PROJECT_SPEC.md` / current roadmap phase  
- [ ] Architecture explained (Phase 2.6)  
- [ ] Docs updated  
- [ ] Tests or verification steps included  
- [ ] No unexplained dependencies  
- [ ] Clear ARES vs PX4 vs Gazebo ownership  
