"""Handle register_spool service action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import HomeAssistantError

from ..const import (
    ATTR_COLOR_HEX,
    ATTR_FINGERPRINT,
    ATTR_FRIENDLY_NAME,
    ATTR_INITIAL_WEIGHT,
    ATTR_MATERIAL,
    ATTR_NAME,
    ATTR_WEIGHT,
    LOGGER,
)
from ..data import SpoolRegistrationData

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall

    from ..coordinator import VirtualAmsCoordinator


async def async_handle_register_spool(
    coordinator: VirtualAmsCoordinator,
    call: ServiceCall,
) -> None:
    """
    Register or update a spool in the inventory.

    Name and color are auto-detected from the loaded spool sensor if not provided.
    """
    fingerprint: str | None = call.data.get(ATTR_FINGERPRINT)
    name: str | None = call.data.get(ATTR_NAME)
    color_hex: str | None = call.data.get(ATTR_COLOR_HEX)
    material: str = call.data.get(ATTR_MATERIAL, "")
    weight: float = call.data.get(ATTR_WEIGHT, 1000.0)
    initial_weight: float | None = call.data.get(ATTR_INITIAL_WEIGHT)
    friendly_name: str | None = call.data.get(ATTR_FRIENDLY_NAME) or None

    if not fingerprint or not name or not color_hex:
        active = coordinator.get_active_spool()
        if not active:
            msg = "No spool loaded on the printer and no explicit data provided"
            raise HomeAssistantError(msg)
        fingerprint = fingerprint or active[ATTR_FINGERPRINT]
        name = name or active[ATTR_NAME]
        color_hex = color_hex or active[ATTR_COLOR_HEX]
        if not material:
            material = active.get(ATTR_MATERIAL, "")

    LOGGER.debug("Registering spool: fingerprint=%s weight=%.1f", fingerprint, weight)
    await coordinator.register_spool(
        SpoolRegistrationData(
            fingerprint=fingerprint,  # type: ignore[arg-type]
            name=name,  # type: ignore[arg-type]
            color_hex=color_hex,  # type: ignore[arg-type]
            material=material,
            weight=weight,
            initial_weight=initial_weight,
            friendly_name=friendly_name,
        )
    )
