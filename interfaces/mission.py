"""Mission data types (Phase 1–2).

SE idea: a mission is *data*, not flight code.
Other modules only import these types / loaders — they never talk to MAVSDK.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Waypoint:
    """Local NED-style offset from home, altitude above home (AGL)."""

    north_m: float
    east_m: float
    alt_m: float


@dataclass(frozen=True)
class MissionPlan:
    name: str
    takeoff_altitude_m: float
    arrival_threshold_m: float
    waypoints: tuple[Waypoint, ...]
    # Per-waypoint goto timeout → abort RTH if exceeded.
    waypoint_timeout_s: float = 120.0
    # Abort if battery remaining fraction drops below this (0 disables check).
    min_battery_fraction: float = 0.15
    # If True, after waypoints fly to local (0,0) before landing.
    # Planner may already append home; then this can stay False.
    return_home: bool = False
    home_alt_m: float | None = None

    def __post_init__(self) -> None:
        if self.takeoff_altitude_m <= 0:
            raise ValueError("takeoff_altitude_m must be > 0")
        if self.arrival_threshold_m <= 0:
            raise ValueError("arrival_threshold_m must be > 0")
        if not self.waypoints:
            raise ValueError("mission must have at least one waypoint")
        if self.waypoint_timeout_s <= 0:
            raise ValueError("waypoint_timeout_s must be > 0")
        if not (0.0 <= self.min_battery_fraction < 1.0):
            raise ValueError("min_battery_fraction must be in [0, 1)")


def _as_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc


def mission_from_dict(data: dict[str, Any]) -> MissionPlan:
    if not isinstance(data, dict):
        raise ValueError("mission root must be a JSON object")

    name = str(data.get("name", "unnamed"))
    takeoff = _as_float(data.get("takeoff_altitude_m", 5.0), "takeoff_altitude_m")
    threshold = _as_float(data.get("arrival_threshold_m", 1.5), "arrival_threshold_m")

    raw_wps = data.get("waypoints")
    if not isinstance(raw_wps, list) or not raw_wps:
        raise ValueError("waypoints must be a non-empty list")

    waypoints: list[Waypoint] = []
    for i, item in enumerate(raw_wps):
        if not isinstance(item, dict):
            raise ValueError(f"waypoints[{i}] must be an object")
        waypoints.append(
            Waypoint(
                north_m=_as_float(item.get("north_m"), f"waypoints[{i}].north_m"),
                east_m=_as_float(item.get("east_m"), f"waypoints[{i}].east_m"),
                alt_m=_as_float(item.get("alt_m"), f"waypoints[{i}].alt_m"),
            )
        )

    home_alt = data.get("home_alt_m", None)
    return MissionPlan(
        name=name,
        takeoff_altitude_m=takeoff,
        arrival_threshold_m=threshold,
        waypoints=tuple(waypoints),
        waypoint_timeout_s=_as_float(
            data.get("waypoint_timeout_s", 120.0), "waypoint_timeout_s"
        ),
        min_battery_fraction=_as_float(
            data.get("min_battery_fraction", 0.15), "min_battery_fraction"
        ),
        return_home=bool(data.get("return_home", False)),
        home_alt_m=None if home_alt is None else _as_float(home_alt, "home_alt_m"),
    )


def load_mission(path: str | Path) -> MissionPlan:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    return mission_from_dict(data)
