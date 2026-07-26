"""Execute a MissionPlan on a Vehicle.

SE idea: orchestration lives here — not in Vehicle, not in JSON, not in the CLI.

Phase 2 adds:
- optional return_home after waypoints
- waypoint timeout → abort RTH + land
- basic battery fraction check before each waypoint
"""

from __future__ import annotations

import asyncio

from control.vehicle import Vehicle
from interfaces.mission import MissionPlan


class MissionAbort(RuntimeError):
    """Raised internally when the runner decides to abort (battery / timeout)."""


async def run_mission(vehicle: Vehicle, mission: MissionPlan) -> None:
    print(f"=== Mission: {mission.name} ({len(mission.waypoints)} waypoints) ===")

    await vehicle.connect()
    await vehicle.wait_ready()
    await vehicle.capture_home()

    await vehicle.arm()
    await vehicle.takeoff(mission.takeoff_altitude_m)
    # Allow climb before first goto (PX4 needs a short settle).
    await asyncio.sleep(8)

    aborted = False
    abort_reason = ""
    try:
        for i, wp in enumerate(mission.waypoints, start=1):
            await _ensure_battery(vehicle, mission)
            print(f"-- Waypoint {i}/{len(mission.waypoints)}")
            await vehicle.goto_ned(wp.north_m, wp.east_m, wp.alt_m)
            try:
                await vehicle.wait_arrival(
                    wp.north_m,
                    wp.east_m,
                    wp.alt_m,
                    threshold_m=mission.arrival_threshold_m,
                    timeout_s=mission.waypoint_timeout_s,
                )
            except TimeoutError as exc:
                raise MissionAbort(f"waypoint {i} timeout: {exc}") from exc

        if mission.return_home:
            await _fly_home(vehicle, mission, label="Return-to-home")

    except MissionAbort as exc:
        aborted = True
        abort_reason = str(exc)
        print(f"!! ABORT: {abort_reason}")
        await _emergency_rth_and_land(vehicle, mission)
        print("MISSION_ABORT_RTH")
        return

    await vehicle.land()
    await vehicle.wait_landed()
    await asyncio.sleep(2)
    print("MISSION_OK")


async def _ensure_battery(vehicle: Vehicle, mission: MissionPlan) -> None:
    if mission.min_battery_fraction <= 0:
        return
    async for bat in vehicle.drone.telemetry.battery():
        frac = float(bat.remaining_percent)
        # MAVSDK: remaining_percent is typically 0..1; accept 0..100 too.
        if frac > 1.0:
            frac = frac / 100.0
        print(f"  battery≈{frac:.0%}")
        if frac < mission.min_battery_fraction:
            raise MissionAbort(
                f"battery {frac:.0%} < min {mission.min_battery_fraction:.0%}"
            )
        return


async def _fly_home(vehicle: Vehicle, mission: MissionPlan, *, label: str) -> None:
    alt = mission.home_alt_m or mission.takeoff_altitude_m
    print(f"-- {label} → N=0 E=0 alt={alt:.1f}")
    await vehicle.goto_ned(0.0, 0.0, alt)
    await vehicle.wait_arrival(
        0.0,
        0.0,
        alt,
        threshold_m=mission.arrival_threshold_m,
        timeout_s=mission.waypoint_timeout_s,
    )


async def _emergency_rth_and_land(vehicle: Vehicle, mission: MissionPlan) -> None:
    """Best-effort home then land (may be a straight line — abort path)."""
    try:
        await _fly_home(vehicle, mission, label="Emergency RTH")
    except Exception as exc:
        print(f"Emergency RTH goto failed ({type(exc).__name__}: {exc}); landing")
    try:
        await vehicle.land()
        await vehicle.wait_landed()
    except Exception as exc:
        print(f"Land after abort failed: {type(exc).__name__}: {exc}")
    await asyncio.sleep(1)
