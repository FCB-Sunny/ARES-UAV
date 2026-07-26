"""Unit tests for mission schema (no SITL required)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from interfaces.mission import load_mission, mission_from_dict


class MissionSchemaTests(unittest.TestCase):
    def test_square_demo_loads(self) -> None:
        plan = load_mission(ROOT / "missions" / "square_demo.json")
        self.assertEqual(plan.name, "square_demo")
        self.assertEqual(len(plan.waypoints), 4)
        self.assertEqual(plan.waypoints[0].north_m, 8.0)

    def test_rejects_empty_waypoints(self) -> None:
        with self.assertRaises(ValueError):
            mission_from_dict({"name": "bad", "waypoints": []})

    def test_rejects_bad_number(self) -> None:
        with self.assertRaises(ValueError):
            mission_from_dict(
                {
                    "name": "bad",
                    "waypoints": [{"north_m": "x", "east_m": 0, "alt_m": 5}],
                }
            )

    def test_roundtrip_temp_file(self) -> None:
        payload = {
            "name": "tiny",
            "takeoff_altitude_m": 4,
            "arrival_threshold_m": 1.5,
            "waypoints": [{"north_m": 1, "east_m": 2, "alt_m": 4}],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "m.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            plan = load_mission(path)
            self.assertEqual(plan.waypoints[0].east_m, 2.0)


if __name__ == "__main__":
    unittest.main()
