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
) -> NavigationRequest:
    return NavigationRequest(
        name="test",
        takeoff_altitude_m=5.0,
        arrival_threshold_m=2.0,
        altitude_m=5.0,
        start=XY(0.0, 0.0),
        goal=goal or XY(20.0, 16.0),
        grid=GridBounds(
            resolution_m=2.0,
            north_min=-2.0,
            north_max=24.0,
            east_min=-2.0,
            east_max=20.0,
        ),
        obstacles=obstacles,
    )


class PlannerTests(unittest.TestCase):
    def test_navigate_demo_loads_and_plans(self) -> None:
        req = load_navigation(ROOT / "missions" / "navigate_demo.json")
        plan = plan_mission(req)
        self.assertGreaterEqual(len(plan.waypoints), 1)
        last = plan.waypoints[-1]
        self.assertAlmostEqual(last.north_m, req.goal.north_m, places=5)
        self.assertAlmostEqual(last.east_m, req.goal.east_m, places=5)

    def test_path_avoids_obstacle_blocking_straight_line(self) -> None:
        obs = (ObstacleCircle(north_m=10.0, east_m=8.0, radius_m=4.0),)
        plan = plan_mission(_req(obstacles=obs))
        # Straight line would go near obstacle center; path should detour.
        for wp in plan.waypoints[:-1]:
            dist = ((wp.north_m - 10.0) ** 2 + (wp.east_m - 8.0) ** 2) ** 0.5
            self.assertGreater(dist, 3.5, msg=f"waypoint inside obstacle: {wp}")

    def test_impossible_goal_raises(self) -> None:
        # Horizontal wall of circles blocking north progress to the goal.
        walls = tuple(
            ObstacleCircle(north_m=10.0, east_m=float(e), radius_m=1.8)
            for e in range(-2, 21, 2)
        )
        with self.assertRaises(PlanningError):
            plan_mission(_req(obstacles=walls, goal=XY(20.0, 16.0)))

    def test_start_in_obstacle_raises(self) -> None:
        with self.assertRaises(PlanningError):
            plan_mission(
                _req(obstacles=(ObstacleCircle(0.0, 0.0, 3.0),))
            )


if __name__ == "__main__":
    unittest.main()
