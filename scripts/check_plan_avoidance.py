#!/usr/bin/env python3
"""Check that a planned path keeps safety margin from obstacles (no SITL)."""

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
    p = argparse.ArgumentParser(description="Verify planner keeps safety margin")
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
    print(f"safety_radius_m={req.safety_radius_m}")
    for i, obs in enumerate(req.obstacles, 1):
        print(
            f"Obstacle {i}: center=({obs.north_m:.1f},{obs.east_m:.1f}) "
            f"r={obs.radius_m:.1f} m  keep-out>={obs.radius_m + req.safety_radius_m:.1f} m"
        )

    ok = True
    print("\nWaypoint clearance (margin above physical radius):")
    for i, wp in enumerate(plan.waypoints, 1):
        worst_margin = float("inf")
        for obs in req.obstacles:
            d = math.hypot(wp.north_m - obs.north_m, wp.east_m - obs.east_m)
            worst_margin = min(worst_margin, d - obs.radius_m)
        safe = worst_margin + 1e-6 >= req.safety_radius_m
        ok = ok and safe
        status = "SAFE" if safe else "TOO CLOSE"
        print(
            f"  {i}: N={wp.north_m:6.1f} E={wp.east_m:6.1f}  "
            f"margin={worst_margin:5.2f} m  need>={req.safety_radius_m:.1f}  {status}"
        )

    grid = build_grid(
        req.grid,
        req.obstacles,
        inflation_m=req.safety_radius_m,
    )
    start_c = grid.world_to_cell(req.start)
    goal_c = grid.world_to_cell(req.goal)
    cells = astar(grid, start_c, goal_c) or []
    path_cells = set(cells)

    print("\nInflated grid (N up, E right)  . free  # keep-out  S start  G goal  * path")
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
        print("CHECK_OK: path respects safety_radius_m")
        return 0
    print("CHECK_FAIL: path closer than safety_radius_m")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
