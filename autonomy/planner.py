"""A* path planner: NavigationRequest → MissionPlan.

SE idea: autonomy outputs the same MissionPlan that Phase 1 already flies.
control/ does not change; only the *source* of waypoints changes.
"""

from __future__ import annotations

import heapq
import math

from autonomy.grid_map import GridMap, build_grid
from interfaces.mission import MissionPlan, Waypoint
from interfaces.navigation import NavigationRequest, XY


class PlanningError(RuntimeError):
    """Raised when no path exists or start/goal is invalid."""


def plan_mission(request: NavigationRequest) -> MissionPlan:
    # Inflate obstacles so the *vehicle* (not just the path center) stays clear.
    # PX4 goto also cuts corners between waypoints — extra margin helps.
    grid = build_grid(
        request.grid,
        request.obstacles,
        inflation_m=request.safety_radius_m,
    )
    start_cell = grid.world_to_cell(request.start)
    goal_cell = grid.world_to_cell(request.goal)

    if not grid.is_free(*start_cell):
        raise PlanningError(f"start is blocked or out of bounds: {request.start}")
    if not grid.is_free(*goal_cell):
        raise PlanningError(f"goal is blocked or out of bounds: {request.goal}")

    cells = astar(grid, start_cell, goal_cell)
    if cells is None:
        raise PlanningError("no path from start to goal")

    simplified = _simplify_cells(grid, cells)
    waypoints = _cells_to_waypoints(grid, simplified, request)
    _assert_clearance(waypoints, request)

    return MissionPlan(
        name=request.name,
        takeoff_altitude_m=request.takeoff_altitude_m,
        arrival_threshold_m=request.arrival_threshold_m,
        waypoints=tuple(waypoints),
    )


def _assert_clearance(
    waypoints: list[Waypoint],
    request: NavigationRequest,
) -> None:
    """Fail closed if any waypoint or segment sample violates keep-out."""
    samples = _path_samples(request.start, waypoints)
    for pt in samples:
        for obs in request.obstacles:
            required = obs.radius_m + request.safety_radius_m
            d = math.hypot(pt.north_m - obs.north_m, pt.east_m - obs.east_m)
            if d < required:
                raise PlanningError(
                    f"path too close to obstacle at N={pt.north_m:.1f} E={pt.east_m:.1f} "
                    f"(dist={d:.2f} m < required {required:.2f} m)"
                )


def _path_samples(
    start: XY,
    waypoints: list[Waypoint],
    *,
    step_m: float = 1.0,
) -> list[XY]:
    pts = [start] + [XY(wp.north_m, wp.east_m) for wp in waypoints]
    out: list[XY] = []
    for a, b in zip(pts, pts[1:]):
        out.append(a)
        length = math.hypot(b.north_m - a.north_m, b.east_m - a.east_m)
        n = max(1, int(math.ceil(length / step_m)))
        for i in range(1, n):
            t = i / n
            out.append(
                XY(
                    north_m=a.north_m + t * (b.north_m - a.north_m),
                    east_m=a.east_m + t * (b.east_m - a.east_m),
                )
            )
    if pts:
        out.append(pts[-1])
    return out


def astar(
    grid: GridMap,
    start: tuple[int, int],
    goal: tuple[int, int],
) -> list[tuple[int, int]] | None:
    """8-connected A* on the occupancy grid. Returns cell path or None."""

    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    open_heap: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(open_heap, (0.0, start))
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], float] = {start: 0.0}

    neighbors = (
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    )

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            return _reconstruct(came_from, current)

        cr, cc = current
        for dr, dc in neighbors:
            nr, nc = cr + dr, cc + dc
            if not grid.is_free(nr, nc):
                continue
            step = math.hypot(dr, dc)
            tentative = g_score[current] + step
            neighbor = (nr, nc)
            if tentative >= g_score.get(neighbor, float("inf")):
                continue
            came_from[neighbor] = current
            g_score[neighbor] = tentative
            f = tentative + heuristic(neighbor, goal)
            heapq.heappush(open_heap, (f, neighbor))

    return None


def _reconstruct(
    came_from: dict[tuple[int, int], tuple[int, int]],
    current: tuple[int, int],
) -> list[tuple[int, int]]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def _line_of_sight(grid: GridMap, a: tuple[int, int], b: tuple[int, int]) -> bool:
    """Bresenham-style check that all cells on the segment are free."""
    r0, c0 = a
    r1, c1 = b
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        if not grid.is_free(r, c):
            return False
        if (r, c) == (r1, c1):
            return True
        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r += sr
        if e2 < dr:
            err += dr
            c += sc


def _simplify_cells(
    grid: GridMap, cells: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """Keep corners only (string-pull) so the drone gets fewer gotos."""
    if len(cells) <= 2:
        return cells
    out = [cells[0]]
    i = 0
    while i < len(cells) - 1:
        j = len(cells) - 1
        while j > i + 1:
            if _line_of_sight(grid, cells[i], cells[j]):
                break
            j -= 1
        out.append(cells[j])
        i = j
    return out


def _cells_to_waypoints(
    grid: GridMap,
    cells: list[tuple[int, int]],
    request: NavigationRequest,
) -> list[Waypoint]:
    # Skip the start cell (already takeoff near home); keep goal exactly.
    points: list[XY] = []
    for cell in cells[1:]:
        points.append(grid.cell_to_world(*cell))
    if not points:
        points.append(request.goal)
    else:
        # Snap last waypoint to exact goal coordinates.
        points[-1] = request.goal

    return [
        Waypoint(north_m=p.north_m, east_m=p.east_m, alt_m=request.altitude_m)
        for p in points
    ]
