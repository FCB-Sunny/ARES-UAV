#!/usr/bin/env python3
"""Check that a planned path stays outside JSON obstacles (no SITL)."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from autonomy.grid_map import build_grid
from autonomy.planner import PlanningError, _simplify_cells, astar, plan_mission
from interfaces.navigation import load_navigation


def main() -> int:
    p = argparse.ArgumentParser(description="Verify planner avoids obstacles")
    p.add_argument(
        "navigation",
        nargs="?",
        default=str(ROOT / "missions" / "navigate_demo.json"),
    )
    args = p.parse_args()

    req = load_navigation(args.navigation)
    try:
        plan = plan_mission(req)
    except PlanningError as exc:
        print(f"PLAN FAIL: {exc}")
        return 1

    print(f"Mission: {plan.name}  ({len(plan.waypoints)} waypoints)")
    print(f"Start={req.start}  Goal={req.goal}")
    for i, obs in enumerate(req.obstacles, 1):
        print(
            f"Obstacle {i}: center=({obs.north_m:.1f},{obs.east_m:.1f}) "
            f"r={obs.radius_m:.1f} m"
        )

    ok = True
    print("\nWaypoint clearance:")
    for i, wp in enumerate(plan.waypoints, 1):
        worst = float("inf")
        for obs in req.obstacles:
            d = math.hypot(wp.north_m - obs.north_m, wp.east_m - obs.east_m)
            worst = min(worst, d - obs.radius_m)
        safe = worst > 0
        ok = ok and safe
        status = "SAFE" if safe else "INSIDE"
        print(
            f"  {i}: N={wp.north_m:6.1f} E={wp.east_m:6.1f}  "
            f"margin={worst:5.2f} m  {status}"
        )

    grid = build_grid(req.grid, req.obstacles)
    start_c = grid.world_to_cell(req.start)
    goal_c = grid.world_to_cell(req.goal)
    cells = astar(grid, start_c, goal_c) or []
    path_cells = set(cells)

    print("\nGrid (N up, E right)  . free  # obs  S start  G goal  * path")
    for row in range(grid.n_rows - 1, -1, -1):
        chars: list[str] = []
        for col in range(grid.n_cols):
            if (row, col) == start_c:
                ch = "S"
            elif (row, col) == goal_c:
                ch = "G"
            elif grid.occupied[row][col]:
                ch = "#"
            elif (row, col) in path_cells:
                ch = "*"
            else:
                ch = "."
            chars.append(ch)
        print("".join(chars))

    simp = _simplify_cells(grid, cells)
    print(f"\nRaw cells={len(cells)}  simplified={len(simp)}")
    if ok:
        print("CHECK_OK: all waypoints outside obstacle circles")
        return 0
    print("CHECK_FAIL: at least one waypoint inside an obstacle")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
