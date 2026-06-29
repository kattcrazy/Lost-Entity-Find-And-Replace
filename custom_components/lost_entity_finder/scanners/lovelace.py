"""Scan Lovelace dashboards for tracked old entity IDs."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN
from homeassistant.components.lovelace.const import ConfigNotFound
from homeassistant.core import HomeAssistant

from ..models import ReferenceHit
from ..util import extract_entities_from_value


async def async_scan(
    hass: HomeAssistant, tracked: set[str]
) -> dict[str, list[ReferenceHit]]:
    """Scan dashboards."""
    hits: dict[str, list[ReferenceHit]] = {}
    if LOVELACE_DOMAIN not in hass.data:
        return hits

    lovelace_data = hass.data[LOVELACE_DOMAIN]
    dashboards = getattr(lovelace_data, "dashboards", None)
    if dashboards is None:
        return hits

    for dashboard in dashboards.values():
        url_path = dashboard.url_path or "lovelace"
        title = url_path
        if dashboard.config:
            title = dashboard.config.get("title", url_path)

        try:
            config = await dashboard.async_load(force=False)
        except ConfigNotFound:
            continue

        extracted = await _async_extract_entities(hass, config, tracked)
        for entity_id, view_path in extracted.items():
            if entity_id not in tracked:
                continue
            hit = ReferenceHit(
                resource_type="dashboard",
                label=title,
                edit_url=f"/{url_path}/{view_path}?edit=1",
                resource_id=url_path,
                extra={"view_path": view_path},
            )
            hits.setdefault(entity_id, []).append(hit)

    return hits


async def _async_extract_entities(
    hass: HomeAssistant, config: dict[str, Any], tracked: set[str]
) -> dict[str, int | str]:
    """Extract entity IDs mapped to view path."""
    entities: dict[str, int | str] = {}
    if not isinstance(config, dict):
        return entities

    views = config.get("views")
    if isinstance(views, list):
        for view_index, view in enumerate(views):
            if not isinstance(view, dict):
                continue
            view_path: int | str = view.get("path") or view_index
            found = await extract_entities_from_value(hass, view, tracked)
            for entity_id in found:
                entities.setdefault(entity_id, view_path)
        return entities

    found = await extract_entities_from_value(hass, config, tracked)
    for entity_id in found:
        entities.setdefault(entity_id, 0)
    return entities
