from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import flood_inundation as fi


class FloodInundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dem = np.array(
            [
                [30.0, 35.0, 40.0],
                [45.0, 50.0, 55.0],
                [60.0, 65.0, 70.0],
            ]
        )

    def test_calculate_flood_mask_depth_and_percentage(self) -> None:
        mask, depth, pct = fi.calculate_flood(self.dem, 50.0)
        self.assertEqual(mask.sum(), 4)
        self.assertAlmostEqual(pct, 4 / 9 * 100)
        self.assertAlmostEqual(depth.max(), 20.0)
        self.assertTrue(np.all(depth[~mask] == 0.0))

    def test_no_flood_below_minimum_elevation(self) -> None:
        mask, depth, pct = fi.calculate_flood(self.dem, 20.0)
        self.assertFalse(mask.any())
        self.assertEqual(depth.max(), 0.0)
        self.assertEqual(pct, 0.0)

    def test_full_flood_above_maximum_elevation(self) -> None:
        mask, depth, pct = fi.calculate_flood(self.dem, 80.0)
        self.assertTrue(mask.all())
        self.assertAlmostEqual(depth.max(), 50.0)
        self.assertEqual(pct, 100.0)

    def test_flood_percentage_is_monotonic(self) -> None:
        levels = np.arange(30, 75, 5)
        _, percentages = fi.simulate_rising_water(self.dem, levels)
        self.assertTrue(np.all(np.diff(percentages) >= 0.0))

    def test_flood_volume(self) -> None:
        _, depth, _ = fi.calculate_flood(self.dem, 50.0)
        self.assertAlmostEqual(fi.calculate_flood_volume(depth, cell_area=900.0), depth.sum() * 900.0)

    def test_building_barriers_raise_selected_cells(self) -> None:
        footprints = [(slice(0, 1), slice(0, 2))]
        blocked = fi.add_building_barriers(self.dem, footprints)
        self.assertTrue(np.all(blocked[0, 0:2] > self.dem.max()))
        self.assertEqual(blocked[1, 1], self.dem[1, 1])

    def test_visualization_file_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "flood.png"
            mask, depth, _ = fi.calculate_flood(self.dem, 50.0)
            fi.visualize_flood(self.dem, mask, depth, 50.0, out)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
