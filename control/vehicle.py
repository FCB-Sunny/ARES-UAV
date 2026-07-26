"""Thin MAVSDK wrapper — the only module that talks to PX4.

SE idea: hide SDK details behind a small Vehicle API.
Mission logic should call vehicle.goto_ned(...), not mavsdk internals.
"""

from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass

from mavsdk import System


@dataclass
class HomePosition:
    latitude_deg: float
    longitude_deg: float
    absolute_altitude_m: float


class Vehicle:
    def __init__(self, system_address: str = "udpin://0.0.0.0:14540") -> None:
        self._address = system_address
        self._drone = System()
        self._home: HomePosition | None = None

    @property
    def drone(self) -> System:
        return self._drone

    async def connect(self, timeout_s: float = 60) -> None:
        print(f"Connecting to {self._address} ...")
        await self._drone.connect(system_address=self._address)

        deadline = asyncio.get_event_loop().time() + timeout_s
        async for state in self._drone.core.connection_state():
            if state.is_connected:
                print("Connected")
                return
            if asyncio.get_event_loop().time() > deadline:
                raise TimeoutError("Timed out waiting for MAVSDK connection")

    async def wait_ready(self, timeout_s: float = 90) -> None:
        print("Waiting for health/armable...")
        deadline = asyncio.get_event_loop().time() + timeout_s
        async for health in self._drone.telemetry.health():
            print(
                f"  gps={health.is_global_position_ok} "
                f"home={health.is_home_position_ok} "
                f"local={health.is_local_position_ok} "
                f"armable={health.is_armable}"
            )
            if (
                health.is_armable
                or (health.is_global_position_ok and health.is_home_position_ok)
                or (health.is_local_position_ok and health.is_home_position_ok)
            ):
                print("Vehicle ready")
                return
            if asyncio.get_event_loop().time() > deadline:
                raise TimeoutError("Timed out waiting for vehicle health")

    async def capture_home(self, timeout_s: float = 30) -> HomePosition:
        deadline = asyncio.get_event_loop().time() + timeout_s
        async for home in self._drone.telemetry.home():
            self._home = HomePosition(
                latitude_deg=home.latitude_deg,
                longitude_deg=home.longitude_deg,
                absolute_altitude_m=home.absolute_altitude_m,
            )
            print(
                f"Home: lat={self._home.latitude_deg:.7f} "
                f"lon={self._home.longitude_deg:.7f} "
                f"alt={self._home.absolute_altitude_m:.1f} m"
            )
            return self._home
        raise TimeoutError("No home position received")

    async def arm(self) -> None:
        print("Arming...")
        await self._drone.action.arm()

    async def takeoff(self, altitude_m: float) -> None:
        print(f"Takeoff to {altitude_m:.1f} m AGL...")
        await self._drone.action.set_takeoff_altitude(altitude_m)
        await self._drone.action.takeoff()

    async def goto_ned(
        self,
        north_m: float,
        east_m: float,
        alt_m: float,
        yaw_deg: float = float("nan"),
    ) -> None:
        """Fly to N/E offset from home at alt_m above home altitude."""
        if self._home is None:
            await self.capture_home()
        assert self._home is not None

        lat, lon = ned_to_latlon(
            self._home.latitude_deg,
            self._home.longitude_deg,
            north_m,
            east_m,
        )
        abs_alt = self._home.absolute_altitude_m + alt_m
        print(
            f"Goto N={north_m:.1f} E={east_m:.1f} alt={alt_m:.1f} "
            f"(lat={lat:.7f}, lon={lon:.7f}, amsl={abs_alt:.1f})"
        )
        await self._drone.action.goto_location(lat, lon, abs_alt, yaw_deg)

    async def wait_arrival(
        self,
        north_m: float,
        east_m: float,
        alt_m: float,
        threshold_m: float,
        timeout_s: float = 120,
    ) -> None:
        if self._home is None:
            await self.capture_home()
        assert self._home is not None

        target_lat, target_lon = ned_to_latlon(
            self._home.latitude_deg,
            self._home.longitude_deg,
            north_m,
            east_m,
        )
        target_abs_alt = self._home.absolute_altitude_m + alt_m

        deadline = asyncio.get_event_loop().time() + timeout_s
        async for pos in self._drone.telemetry.position():
            horiz = haversine_m(
                pos.latitude_deg,
                pos.longitude_deg,
                target_lat,
                target_lon,
            )
            vert = abs(pos.absolute_altitude_m - target_abs_alt)
            dist = math.hypot(horiz, vert)
            print(f"  dist≈{dist:.1f} m (h={horiz:.1f}, v={vert:.1f})")
            if dist <= threshold_m:
                print("Arrived")
                return
            if asyncio.get_event_loop().time() > deadline:
                raise TimeoutError(
                    f"Timed out approaching waypoint (last dist≈{dist:.1f} m)"
                )

    async def land(self) -> None:
        print("Landing...")
        await self._drone.action.land()

    async def wait_landed(self, timeout_s: float = 90) -> None:
        deadline = asyncio.get_event_loop().time() + timeout_s
        async for in_air in self._drone.telemetry.in_air():
            if not in_air:
                print("Landed")
                return
            if asyncio.get_event_loop().time() > deadline:
                print("Land wait timed out (continuing)")
                return
            await asyncio.sleep(0.5)


def ned_to_latlon(
    home_lat_deg: float,
    home_lon_deg: float,
    north_m: float,
    east_m: float,
) -> tuple[float, float]:
    """Small-offset flat-earth conversion (good enough for local SITL demos)."""
    dlat = north_m / 111_111.0
    cos_lat = math.cos(math.radians(home_lat_deg))
    # Avoid divide-by-zero near poles (irrelevant for this sim).
    dlon = east_m / (111_111.0 * max(abs(cos_lat), 1e-6))
    return home_lat_deg + dlat, home_lon_deg + dlon


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 637_1000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
