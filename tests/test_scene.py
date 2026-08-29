"""Unit tests for scene scanner."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bootstrap  # noqa: F401

from homeassistant.helpers.entity_component import DATA_INSTANCES

from lost_entity_finder.scanners import scene as scene_scanner


class SceneScannerTests(unittest.TestCase):
    """Tests for scene entity reference scanning."""

    def test_async_scan_uses_scene_domain_in_data_instances(self) -> None:
        """Scene scanner should look up the scene EntityComponent, not homeassistant."""
        hass = MagicMock()
        scene_entity = MagicMock()
        scene_entity.unique_id = "evening_lights"
        scene_entity.entity_id = "scene.evening_lights"
        scene_entity.name = "Evening Lights"
        scene_entity.referenced_entities = []
        scene_entity.referenced_blueprint = None
        scene_entity.raw_config = {
            "id": "evening_lights",
            "name": "Evening Lights",
            "entities": {"light.living_room": "on"},
        }

        component = MagicMock()
        component.entities = [scene_entity]
        hass.data = {DATA_INSTANCES: {"scene": component}}

        hits = asyncio.run(scene_scanner.async_scan(hass, {"light.living_room"}))

        self.assertIn("light.living_room", hits)
        self.assertEqual(hits["light.living_room"][0].resource_type, "scene")
        self.assertEqual(hits["light.living_room"][0].resource_id, "evening_lights")
        self.assertTrue(hits["light.living_room"][0].auto_replaceable)

    def test_async_scan_skips_when_homeassistant_domain_only(self) -> None:
        """Wrong domain key in DATA_INSTANCES should not produce hits."""
        hass = MagicMock()
        component = MagicMock()
        component.entities = []
        hass.data = {DATA_INSTANCES: {"homeassistant": component}}

        hits = asyncio.run(scene_scanner.async_scan(hass, {"light.living_room"}))

        self.assertEqual(hits, {})


if __name__ == "__main__":
    unittest.main()
