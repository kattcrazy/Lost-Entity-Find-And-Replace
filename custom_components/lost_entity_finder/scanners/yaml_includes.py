"""Scan included YAML config files for tracked entity IDs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from homeassistant.core import HomeAssistant

from ..models import ReferenceHit
from ..util import extract_entities_from_value

_LOGGER = logging.getLogger(__name__)

INCLUDED_YAML_FILES: tuple[tuple[str, str], ...] = (
    ("automations.yaml", "automations.yaml"),
    ("scripts.yaml", "scripts.yaml"),
    ("scenes.yaml", "scenes.yaml"),
    ("sensors.yaml", "sensors.yaml"),
    ("templates.yaml", "templates.yaml"),
)


async def async_scan(
    hass: HomeAssistant, tracked: set[str]
) -> dict[str, list[ReferenceHit]]:
    """Scan common included YAML files that are skipped in merged config scanning."""
    hits: dict[str, list[ReferenceHit]] = {}

    for filename, label in INCLUDED_YAML_FILES:
        path = Path(hass.config.path(filename))
        if not path.is_file():
            continue

        try:
            contents = await hass.async_add_executor_job(path.read_text, "utf-8")
            data = yaml.safe_load(contents)
        except Exception:  # noqa: BLE001 - skip unreadable yaml files
            _LOGGER.debug("Skipping included YAML scan for %s", filename, exc_info=True)
            continue

        if data is None:
            continue

        found = await extract_entities_from_value(hass, data, tracked)
        if not found:
            continue

        hit = ReferenceHit(
            resource_type="yaml_config",
            label=label,
            edit_url="/config/configuration",
            resource_id=f"included_yaml:{filename}",
            extra={"filename": filename},
            auto_replaceable=False,
        )
        for entity_id in found:
            hits.setdefault(entity_id, []).append(hit)

    return hits
