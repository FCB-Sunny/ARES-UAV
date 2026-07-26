"""Mission data types (Phase 1).

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

    def __post_init__(self) -> None:
        if self.takeoff_altitude_m <= 0:
            raise ValueError("takeoff_altitude_m must be > 0")
        if self.arrival_threshold_m <= 0:
            raise ValueError("arrival_threshold_m must be > 0")
        if not self.waypoints:
            raise ValueError("mission must have at least one waypoint")


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

    return MissionPlan(
        name=name,
        takeoff_altitude_m=takeoff,
        arrival_threshold_m=threshold,
        waypoints=tuple(waypoints),
    )


def load_mission(path: str | Path) -> MissionPlan:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    return mission_from_dict(data)
