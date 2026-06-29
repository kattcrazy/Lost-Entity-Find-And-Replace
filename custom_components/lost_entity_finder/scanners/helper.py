"""Scan helper entities for tracked old entity IDs."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import DATA_ENTITY_PLATFORM

from ..models import ReferenceHit
from ..util import extract_entities_from_value

HELPER_DOMAINS = (
    "utility_meter",
    "trend",
    "switch_as_x",
    "integration",
    "min_max",
    "statistics",
    "template",
)

HELPER_CONFIG_ENTRY_DOMAINS = HELPER_DOMAINS


async def async_scan(
    hass: HomeAssistant, tracked: set[str]
) -> dict[str, list[ReferenceHit]]:
    """Scan helpers with source entity references."""
    hits: dict[str, list[ReferenceHit]] = {}
    await _async_scan_entity_platforms(hass, tracked, hits)
    await _async_scan_config_entries(hass, tracked, hits)
    return hits


async def _async_scan_entity_platforms(
    hass: HomeAssistant,
    tracked: set[str],
    hits: dict[str, list[ReferenceHit]],
) -> None:
    """Scan loaded helper entities for source entity references."""
    platforms = hass.data.get(DATA_ENTITY_PLATFORM, {})

    for domain in HELPER_DOMAINS:
        for platform in platforms.get(domain, []):
            for entity in platform.entities.values():
                for source in _get_source_entity_ids(entity):
                    if source not in tracked:
                        continue
                    label = getattr(entity, "name", None) or entity.entity_id
                    hit = ReferenceHit(
                        resource_type="helper",
                        label=label,
                        edit_url="/config/helpers",
                        resource_id=entity.entity_id,
                        extra={"entity_id": entity.entity_id, "source": source},
                        auto_replaceable=False,
                    )
                    hits.setdefault(source, []).append(hit)


async def _async_scan_config_entries(
    hass: HomeAssistant,
    tracked: set[str],
    hits: dict[str, list[ReferenceHit]],
) -> None:
    """Scan helper config entries for tracked source entity references."""
    for domain in HELPER_CONFIG_ENTRY_DOMAINS:
        for entry in hass.config_entries.async_entries(domain):
            label = entry.title or entry.entry_id
            hit = ReferenceHit(
                resource_type="helper",
                label=label,
                edit_url="/config/helpers",
                resource_id=entry.entry_id,
                extra={"config_entry_id": entry.entry_id},
                auto_replaceable=False,
            )
            for section in (entry.data, entry.options):
                if not isinstance(section, dict):
                    continue
                found = await extract_entities_from_value(hass, section, tracked)
                for entity_id in found:
                    hits.setdefault(entity_id, []).append(
                        ReferenceHit(
                            resource_type=hit.resource_type,
                            label=hit.label,
                            edit_url=hit.edit_url,
                            resource_id=hit.resource_id,
                            extra={**hit.extra, "source": entity_id},
                            auto_replaceable=hit.auto_replaceable,
                        )
                    )


def _get_source_entity_ids(entity: object) -> list[str]:
    """Return source entity IDs from a helper entity when available."""
    sources: list[str] = []
    for attr in (
        "source_entity_id",
        "_source_entity_id",
        "_sensor_source_id",
        "source",
    ):
        value = getattr(entity, attr, None)
        if isinstance(value, str):
            sources.append(value)

    for attr in ("_entity_ids", "entity_ids"):
        value = getattr(entity, attr, None)
        if isinstance(value, list):
            sources.extend(item for item in value if isinstance(item, str))

    return sources
