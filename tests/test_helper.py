"""Unit tests for helper scanner."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bootstrap  # noqa: F401

from lost_entity_finder.scanners import helper


class HelperScannerTests(unittest.TestCase):
    """Tests for helper entity reference scanning."""

    def test_get_source_entity_ids_reads_platform_attributes(self) -> None:
        """Helper scanner should read common source attribute names."""
        entity = MagicMock()
        entity.source_entity_id = "sensor.power"
        entity._entity_ids = ["sensor.a", "sensor.b"]
        self.assertEqual(
            helper._get_source_entity_ids(entity),
            ["sensor.power", "sensor.a", "sensor.b"],
        )

    def test_get_source_entity_ids_reads_utility_meter_attribute(self) -> None:
        """Utility meter helpers expose _sensor_source_id."""
        entity = MagicMock(spec=[])
        entity._sensor_source_id = "sensor.energy"
        self.assertEqual(helper._get_source_entity_ids(entity), ["sensor.energy"])

    async def _async_scan_config_entry(self) -> dict[str, list]:
        """Run async_scan with a mocked helper config entry."""
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "entry123"
        entry.title = "Kitchen Meter"
        entry.data = {"source_sensor": "sensor.kitchen_energy"}
        entry.options = {}
        hass.config_entries.async_entries.return_value = [entry]
        hass.data = {}
        tracked = {"sensor.kitchen_energy"}
        return await helper.async_scan(hass, tracked)

    def test_async_scan_finds_config_entry_source(self) -> None:
        """Config-entry helpers should be detected."""
        hits = asyncio.run(self._async_scan_config_entry())
        self.assertIn("sensor.kitchen_energy", hits)
        self.assertEqual(hits["sensor.kitchen_energy"][0].resource_type, "helper")
        self.assertEqual(hits["sensor.kitchen_energy"][0].label, "Kitchen Meter")


if __name__ == "__main__":
    unittest.main()
