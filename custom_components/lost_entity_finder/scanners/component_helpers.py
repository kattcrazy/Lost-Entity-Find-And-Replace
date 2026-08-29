"""Shared helpers for automation/script/scene scanners."""

from __future__ import annotations

from typing import Any


def is_auto_replaceable_component_entity(entity: Any) -> bool:
    """Return True when a component entity can be updated via the config editor."""
    if getattr(entity, "unique_id", None) is None:
        return False
    if getattr(entity, "referenced_blueprint", None):
        return False
    return True
