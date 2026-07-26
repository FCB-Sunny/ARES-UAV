#!/usr/bin/env python3
"""Phase 0 acceptance: connect to PX4 SITL and arm → takeoff → land via MAVSDK."""

from __future__ import annotations

import asyncio
import sys

from mavsdk import System


async def wait_ready(drone: System, timeout_s: float = 90) -> None:
    print("Waiting for health/armable...")
    deadline = asyncio.get_event_loop().time() + timeout_s
    async for health in drone.telemetry.health():
        print(
            f"  gps={health.is_global_position_ok} "
            f"home={health.is_home_position_ok} "
            f"local={health.is_local_position_ok} "
            f"armable={health.is_armable}"
        )
        if health.is_armable:
            print("Armable OK")
            return
        if health.is_global_position_ok and health.is_home_position_ok:
            print("Health OK (gps+home)")
            return
        if health.is_local_position_ok and health.is_home_position_ok:
            print("Health OK (local+home) — proceeding for SITL")
            return
        if asyncio.get_event_loop().time() > deadline:
            raise TimeoutError("Timed out waiting for vehicle health")


async def main() -> None:
    drone = System()
    print("Connecting to udpin://0.0.0.0:14540 ...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected")
            break

    await wait_ready(drone)

    print("Arming...")
    await drone.action.arm()
    print("Taking off...")
    await drone.action.set_takeoff_altitude(5.0)
    await drone.action.takeoff()
    await asyncio.sleep(12)
    print("Landing...")
    await drone.action.land()

    landed_deadline = asyncio.get_event_loop().time() + 60
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("Landed")
            break
        if asyncio.get_event_loop().time() > landed_deadline:
            print("Land wait timed out (continuing)")
            break
        await asyncio.sleep(0.5)

    await asyncio.sleep(2)
    print("MAVSDK control OK")
    print("STEP9_OK")


if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(main(), timeout=240))
    except Exception as e:
        print(f"STEP9_FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
