"""Unit tests for component scanner helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bootstrap  # noqa: F401

from lost_entity_finder.scanners.component_helpers import is_auto_replaceable_component_entity


class ComponentHelperTests(unittest.TestCase):
    """Tests for auto-replace eligibility on component entities."""

    def test_unique_id_without_raw_config_is_auto_replaceable(self) -> None:
        """UI-created entities should be auto-replaceable when they have an id."""
        entity = MagicMock()
        entity.unique_id = "morning_routine"
        entity.raw_config = None
        entity.referenced_blueprint = None

        self.assertTrue(is_auto_replaceable_component_entity(entity))

    def test_blueprint_entities_are_not_auto_replaceable(self) -> None:
        """Blueprint-backed entities must stay manual."""
        entity = MagicMock()
        entity.unique_id = "morning_routine"
        entity.raw_config = {"id": "morning_routine"}
        entity.referenced_blueprint = {"path": "author/blueprint.yaml"}

        self.assertFalse(is_auto_replaceable_component_entity(entity))

    def test_entities_without_unique_id_are_not_auto_replaceable(self) -> None:
        """Entities without a stable id cannot be updated via the config editor."""
        entity = MagicMock()
        entity.unique_id = None
        entity.raw_config = {"alias": "Temporary"}

        self.assertFalse(is_auto_replaceable_component_entity(entity))


if __name__ == "__main__":
    unittest.main()
