"""Inventory sensor for virtual_ams."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

from ..const import ATTR_SPOOLS
from ..entity import VirtualAmsEntity

if TYPE_CHECKING:
    from ..coordinator import VirtualAmsCoordinator


class VirtualAmsInventorySensor(VirtualAmsEntity, SensorEntity):
    """Sensor exposing the full spool inventory."""

    _attr_icon = "mdi:package-variant"
    _attr_translation_key = "inventory"

    def __init__(self, coordinator: VirtualAmsCoordinator) -> None:
        """Initialize the inventory sensor."""
        super().__init__(coordinator, "inventory")

    @property
    def native_value(self) -> int:
        """Return the number of spools in inventory."""
        return len(self._coordinator.inventory)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the full inventory as extra attributes."""
        return {ATTR_SPOOLS: self._coordinator.inventory}
