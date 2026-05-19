"""Base entity class for virtual_ams."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from ..const import DOMAIN

if TYPE_CHECKING:
    from ..coordinator import VirtualAmsCoordinator


class VirtualAmsEntity(Entity):
    """Base class for all Virtual AMS entities."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, coordinator: VirtualAmsCoordinator, key: str) -> None:
        """Initialize the entity."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="Virtual AMS",
            manufacturer="Virtual AMS",
            model="Filament Inventory Manager",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator updates when added to HA."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self._coordinator.signal,
                self.async_write_ha_state,
            )
        )
