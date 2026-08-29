"""Helpers for resolving loaded Lost Entity Finder config entries."""

from __future__ import annotations

from collections.abc import Iterator

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .manager import EntityFinderManager


def iter_loaded_entries(hass: HomeAssistant) -> Iterator[ConfigEntry]:
    """Yield config entries that finished loading."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.state == ConfigEntryState.LOADED:
            yield entry


def get_loaded_manager(hass: HomeAssistant) -> EntityFinderManager | None:
    """Return the manager from a loaded config entry, if any."""
    for entry in iter_loaded_entries(hass):
        manager = entry.runtime_data
        if isinstance(manager, EntityFinderManager):
            return manager
    return None
