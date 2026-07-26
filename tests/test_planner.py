"""Unit tests for Phase 2 A* planner (no SITL required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from autonomy.planner import PlanningError, plan_mission
from interfaces.navigation import (
    GridBounds,
    NavigationRequest,
    ObstacleCircle,
    XY,
    load_navigation,
)


def _req(
    *,
    obstacles: tuple[ObstacleCircle, ...] = (),
    goal: XY | None = None,
    safety_radius_m: float = 2.5,
) -> NavigationRequest:
    return NavigationRequest(
        name="test",
        takeoff_altitude_m=5.0,
        arrival_threshold_m=2.0,
        altitude_m=5.0,
        start=XY(0.0, 0.0),
        goal=goal or XY(20.0, 16.0),
        grid=GridBounds(
            resolution_m=1.0,
            north_min=-2.0,
            north_max=24.0,
            east_min=-2.0,
            east_max=24.0,
        ),
        obstacles=obstacles,
        safety_radius_m=safety_radius_m,
    )


class PlannerTests(unittest.TestCase):
    def test_navigate_demo_loads_and_plans(self) -> None:
        req = load_navigation(ROOT / "missions" / "navigate_demo.json")
        plan = plan_mission(req)
        self.assertGreaterEqual(len(plan.waypoints), 1)
        last = plan.waypoints[-1]
        self.assertAlmostEqual(last.north_m, req.goal.north_m, places=5)
        self.assertAlmostEqual(last.east_m, req.goal.east_m, places=5)

    def test_path_keeps_safety_margin(self) -> None:
        obs = (ObstacleCircle(north_m=10.0, east_m=8.0, radius_m=4.0),)
        safety = 2.5
        plan = plan_mission(_req(obstacles=obs, safety_radius_m=safety))
        required = 4.0 + safety
        for wp in plan.waypoints:
            dist = ((wp.north_m - 10.0) ** 2 + (wp.east_m - 8.0) ** 2) ** 0.5
            self.assertGreaterEqual(
                dist,
                required - 0.05,
                msg=f"waypoint too close: {wp} dist={dist:.2f}",
            )

    def test_impossible_goal_raises(self) -> None:
        # Solid keep-out band across the full map width.
        walls = tuple(
            ObstacleCircle(north_m=10.0, east_m=float(e), radius_m=1.2)
            for e in range(-2, 25)
        )
        with self.assertRaises(PlanningError):
            plan_mission(_req(obstacles=walls, goal=XY(20.0, 16.0), safety_radius_m=1.0))

    def test_start_in_obstacle_raises(self) -> None:
        with self.assertRaises(PlanningError):
            plan_mission(
                _req(obstacles=(ObstacleCircle(0.0, 0.0, 3.0),), safety_radius_m=0.0)
            )


if __name__ == "__main__":
    unittest.main()
