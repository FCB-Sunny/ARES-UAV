#!/usr/bin/env python3
"""Phase 1 entry: load a mission JSON and fly it via control.Vehicle."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Allow `python scripts/run_waypoint_mission.py` without installing a package.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from control.mission_runner import run_mission
from control.vehicle import Vehicle
from interfaces.mission import load_mission


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fly a Phase-1 waypoint mission")
    p.add_argument(
        "mission",
        nargs="?",
        default=str(ROOT / "missions" / "square_demo.json"),
        help="Path to mission JSON (default: missions/square_demo.json)",
    )
    p.add_argument(
        "--address",
        default="udpin://0.0.0.0:14540",
        help="MAVSDK system address",
    )
    return p.parse_args()


async def main() -> None:
    args = parse_args()
    mission = load_mission(args.mission)
    vehicle = Vehicle(system_address=args.address)
    await run_mission(vehicle, mission)


if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(main(), timeout=600))
    except Exception as e:
        print(f"MISSION_FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
