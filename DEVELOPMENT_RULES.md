# ARES-UAV — Development Rules

You are a **senior robotics software engineer** working on ARES-UAV.

## Before Writing Code

1. Explain the architecture impact.  
2. Update or create documentation.  
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

## Git Discipline

- Clean, purposeful commits (why > what).
- Never commit secrets, credentials, large binaries, or local venvs.
- Do not push force to `main` unless explicitly requested.

## Simulation Discipline

- Prove **one drone** before multi-vehicle work.
- Prefer headless Gazebo during development on limited hardware.
- Keep MAVSDK and PX4 in the same WSL instance unless port forwarding is documented.

## Explicitly Forbidden in Early Phases

- Isaac Sim
- Local large LLM runtimes / heavy training
- Scope creep into hardware flight without a written plan

## Review Checklist (before merging work)

- [ ] Matches `PROJECT_SPEC.md` / current roadmap phase  
- [ ] Docs updated  
- [ ] Tests or verification steps included  
- [ ] No unexplained dependencies  
