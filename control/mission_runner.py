"""Execute a MissionPlan on a Vehicle.

SE idea: orchestration lives here — not in Vehicle, not in JSON, not in the CLI.
"""

from __future__ import annotations

import asyncio

from control.vehicle import Vehicle
from interfaces.mission import MissionPlan


async def run_mission(vehicle: Vehicle, mission: MissionPlan) -> None:
    print(f"=== Mission: {mission.name} ({len(mission.waypoints)} waypoints) ===")

    await vehicle.connect()
    await vehicle.wait_ready()
    await vehicle.capture_home()

    await vehicle.arm()
    await vehicle.takeoff(mission.takeoff_altitude_m)
    # Allow climb before first goto (PX4 needs a short settle).
    await asyncio.sleep(8)

    for i, wp in enumerate(mission.waypoints, start=1):
        print(f"-- Waypoint {i}/{len(mission.waypoints)}")
        await vehicle.goto_ned(wp.north_m, wp.east_m, wp.alt_m)
        await vehicle.wait_arrival(
            wp.north_m,
            wp.east_m,
            wp.alt_m,
            threshold_m=mission.arrival_threshold_m,
        )

    await vehicle.land()
    await vehicle.wait_landed()
    await asyncio.sleep(2)
    print("MISSION_OK")
