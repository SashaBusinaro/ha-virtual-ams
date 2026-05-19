"""Active spool sensor for virtual_ams."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

from ..const import ATTR_DISPLAY_NAME
from ..entity import VirtualAmsEntity

if TYPE_CHECKING:
    from ..coordinator import VirtualAmsCoordinator


class VirtualAmsActiveSpoolSensor(VirtualAmsEntity, SensorEntity):
    """Sensor representing the currently loaded spool."""

    _attr_icon = "mdi:printer-3d-nozzle"
    _attr_translation_key = "active_spool"

    def __init__(self, coordinator: VirtualAmsCoordinator) -> None:
        """Initialize the active spool sensor."""
        super().__init__(coordinator, "active_spool")

    @property
    def native_value(self) -> str | None:
        """Return the display name of the active spool, or None."""
        data = self._coordinator.get_active_spool()
        if not data:
            return None
        return data.get(ATTR_DISPLAY_NAME)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return full spool data as extra attributes."""
        return self._coordinator.get_active_spool()
