"""Navigation request: start/goal (+ optional obstacles) → planner input.

SE idea: this is *what we want*, not *how we fly*.
Planner turns it into a MissionPlan; control/ never sees this type.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class XY:
    north_m: float
    east_m: float


@dataclass(frozen=True)
class ObstacleCircle:
    north_m: float
    east_m: float
    radius_m: float

    def __post_init__(self) -> None:
        if self.radius_m <= 0:
            raise ValueError("obstacle radius_m must be > 0")


@dataclass(frozen=True)
class GridBounds:
    resolution_m: float
    north_min: float
    north_max: float
    east_min: float
    east_max: float

    def __post_init__(self) -> None:
        if self.resolution_m <= 0:
            raise ValueError("resolution_m must be > 0")
        if self.north_max <= self.north_min or self.east_max <= self.east_min:
            raise ValueError("grid bounds must have max > min")


@dataclass(frozen=True)
class NavigationRequest:
    """High-level navigate intent (Phase 2 planner input)."""

    name: str
    takeoff_altitude_m: float
    arrival_threshold_m: float
    altitude_m: float
    start: XY
    goal: XY
    grid: GridBounds
    obstacles: tuple[ObstacleCircle, ...] = ()

    def __post_init__(self) -> None:
        if self.takeoff_altitude_m <= 0 or self.altitude_m <= 0:
            raise ValueError("altitudes must be > 0")
        if self.arrival_threshold_m <= 0:
            raise ValueError("arrival_threshold_m must be > 0")


def _as_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc


def _xy(data: Any, field: str) -> XY:
    if not isinstance(data, dict):
        raise ValueError(f"{field} must be an object")
    return XY(
        north_m=_as_float(data.get("north_m"), f"{field}.north_m"),
        east_m=_as_float(data.get("east_m"), f"{field}.east_m"),
    )


def navigation_from_dict(data: dict[str, Any]) -> NavigationRequest:
    if not isinstance(data, dict):
        raise ValueError("navigation root must be a JSON object")

    grid_raw = data.get("grid")
    if not isinstance(grid_raw, dict):
        raise ValueError("grid must be an object")

    obstacles: list[ObstacleCircle] = []
    for i, item in enumerate(data.get("obstacles") or []):
        if not isinstance(item, dict):
            raise ValueError(f"obstacles[{i}] must be an object")
        obstacles.append(
            ObstacleCircle(
                north_m=_as_float(item.get("north_m"), f"obstacles[{i}].north_m"),
                east_m=_as_float(item.get("east_m"), f"obstacles[{i}].east_m"),
                radius_m=_as_float(item.get("radius_m"), f"obstacles[{i}].radius_m"),
            )
        )

    return NavigationRequest(
        name=str(data.get("name", "unnamed")),
        takeoff_altitude_m=_as_float(
            data.get("takeoff_altitude_m", 5.0), "takeoff_altitude_m"
        ),
        arrival_threshold_m=_as_float(
            data.get("arrival_threshold_m", 2.0), "arrival_threshold_m"
        ),
        altitude_m=_as_float(data.get("altitude_m", 5.0), "altitude_m"),
        start=_xy(data.get("start"), "start"),
        goal=_xy(data.get("goal"), "goal"),
        grid=GridBounds(
            resolution_m=_as_float(grid_raw.get("resolution_m", 2.0), "grid.resolution_m"),
            north_min=_as_float(grid_raw.get("north_min"), "grid.north_min"),
            north_max=_as_float(grid_raw.get("north_max"), "grid.north_max"),
            east_min=_as_float(grid_raw.get("east_min"), "grid.east_min"),
            east_max=_as_float(grid_raw.get("east_max"), "grid.east_max"),
        ),
        obstacles=tuple(obstacles),
    )


def load_navigation(path: str | Path) -> NavigationRequest:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    return navigation_from_dict(data)
