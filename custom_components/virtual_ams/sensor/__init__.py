"""Sensor platform for virtual_ams."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .active_spool import VirtualAmsActiveSpoolSensor
from .inventory import VirtualAmsInventorySensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..data import VirtualAmsConfigEntry

PARALLEL_UPDATES = 0


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: VirtualAmsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Virtual AMS sensor entities."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            VirtualAmsActiveSpoolSensor(coordinator),
            VirtualAmsInventorySensor(coordinator),
        ]
    )
