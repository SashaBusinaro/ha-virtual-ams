"""Handle update_spool service action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import HomeAssistantError

from ..const import (
    ATTR_FINGERPRINT,
    ATTR_FRIENDLY_NAME,
    ATTR_INITIAL_WEIGHT,
    ATTR_MATERIAL,
    ATTR_WEIGHT,
    LOGGER,
)

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall

    from ..coordinator import VirtualAmsCoordinator


async def async_handle_update_spool(
    coordinator: VirtualAmsCoordinator,
    call: ServiceCall,
) -> None:
    """
    Update weight, name or material of an existing spool.

    Fingerprint defaults to the currently loaded spool if not provided.
    """
    fingerprint: str | None = call.data.get(ATTR_FINGERPRINT)

    if not fingerprint:
        fingerprint = coordinator.get_current_fingerprint()
    if not fingerprint:
        msg = "No fingerprint specified and no spool currently loaded"
        raise HomeAssistantError(msg)

    kwargs = {
        key: call.data[key]
        for key in (ATTR_WEIGHT, ATTR_INITIAL_WEIGHT, ATTR_FRIENDLY_NAME, ATTR_MATERIAL)
        if key in call.data
    }
    if not kwargs:
        msg = "At least one field to update must be provided"
        raise HomeAssistantError(msg)

    try:
        LOGGER.debug("Updating spool %s: %s", fingerprint, kwargs)
        await coordinator.update_spool(fingerprint, **kwargs)
    except ValueError as exc:
        raise HomeAssistantError(str(exc)) from exc
