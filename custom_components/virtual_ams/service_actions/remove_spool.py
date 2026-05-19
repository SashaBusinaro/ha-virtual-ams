"""Handle remove_spool service action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..const import ATTR_FINGERPRINT, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall

    from ..coordinator import VirtualAmsCoordinator


async def async_handle_remove_spool(
    coordinator: VirtualAmsCoordinator,
    call: ServiceCall,
) -> None:
    """Remove a spool from the inventory."""
    fingerprint: str = call.data[ATTR_FINGERPRINT]
    LOGGER.debug("Removing spool %s from inventory", fingerprint)
    await coordinator.remove_spool(fingerprint)
