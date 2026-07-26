#!/usr/bin/env python3
"""Phase 2 entry: plan a path from navigation JSON, then fly via control/."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from autonomy.planner import PlanningError, plan_mission
from interfaces.navigation import load_navigation


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plan + fly a Phase-2 navigation request")
    p.add_argument(
        "navigation",
        nargs="?",
        default=str(ROOT / "missions" / "navigate_demo.json"),
        help="Path to navigation JSON (default: missions/navigate_demo.json)",
    )
    p.add_argument(
        "--address",
        default="udpin://0.0.0.0:14540",
        help="MAVSDK system address",
    )
    p.add_argument(
        "--plan-only",
        action="store_true",
        help="Print planned waypoints and exit (no SITL)",
    )
    return p.parse_args()


async def main() -> None:
    args = parse_args()
    request = load_navigation(args.navigation)
    try:
        mission = plan_mission(request)
    except PlanningError as exc:
        raise SystemExit(f"MISSION_FAIL: PlanningError: {exc}") from exc

    print(f"Planned {len(mission.waypoints)} waypoints:")
    for i, wp in enumerate(mission.waypoints, start=1):
        print(f"  {i}: N={wp.north_m:.1f} E={wp.east_m:.1f} alt={wp.alt_m:.1f}")

    if args.plan_only:
        print("PLAN_OK")
        return

    # Lazy import: MAVSDK only needed when actually flying.
    from control.mission_runner import run_mission
    from control.vehicle import Vehicle

    vehicle = Vehicle(system_address=args.address)
    await run_mission(vehicle, mission)


if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(main(), timeout=600))
    except SystemExit:
        raise
    except Exception as e:
        print(f"MISSION_FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
