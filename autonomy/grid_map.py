"""2D occupancy grid in local N/E meters (Phase 2).

SE idea: map is a pure data structure. No MAVSDK, no Gazebo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from interfaces.navigation import GridBounds, ObstacleCircle, XY


@dataclass
class GridMap:
    bounds: GridBounds
    # True = occupied / blocked
    occupied: list[list[bool]]

    @property
    def n_rows(self) -> int:
        return len(self.occupied)

    @property
    def n_cols(self) -> int:
        return len(self.occupied[0]) if self.occupied else 0

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.n_rows and 0 <= col < self.n_cols

    def is_free(self, row: int, col: int) -> bool:
        return self.in_bounds(row, col) and not self.occupied[row][col]

    def world_to_cell(self, point: XY) -> tuple[int, int]:
        res = self.bounds.resolution_m
        col = int((point.east_m - self.bounds.east_min) / res)
        row = int((point.north_m - self.bounds.north_min) / res)
        return row, col

    def cell_to_world(self, row: int, col: int) -> XY:
        res = self.bounds.resolution_m
        north = self.bounds.north_min + (row + 0.5) * res
        east = self.bounds.east_min + (col + 0.5) * res
        return XY(north_m=north, east_m=east)


def build_grid(bounds: GridBounds, obstacles: tuple[ObstacleCircle, ...] = ()) -> GridMap:
    res = bounds.resolution_m
    n_rows = max(1, int(math.ceil((bounds.north_max - bounds.north_min) / res)))
    n_cols = max(1, int(math.ceil((bounds.east_max - bounds.east_min) / res)))
    occupied = [[False for _ in range(n_cols)] for _ in range(n_rows)]

    grid = GridMap(bounds=bounds, occupied=occupied)
    for obs in obstacles:
        _stamp_circle(grid, obs)
    return grid


def _stamp_circle(grid: GridMap, obs: ObstacleCircle) -> None:
    for row in range(grid.n_rows):
        for col in range(grid.n_cols):
            cell = grid.cell_to_world(row, col)
            dist = math.hypot(cell.north_m - obs.north_m, cell.east_m - obs.east_m)
            if dist <= obs.radius_m:
                grid.occupied[row][col] = True
