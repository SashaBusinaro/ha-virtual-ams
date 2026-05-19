"""Service actions for virtual_ams."""

from __future__ import annotations

from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError

from ..const import (
    ATTR_COLOR_HEX,
    ATTR_FINGERPRINT,
    ATTR_FRIENDLY_NAME,
    ATTR_INITIAL_WEIGHT,
    ATTR_MATERIAL,
    ATTR_NAME,
    ATTR_WEIGHT,
    DOMAIN,
    LOGGER,
)
from .register_spool import async_handle_register_spool
from .remove_spool import async_handle_remove_spool
from .update_spool import async_handle_update_spool

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from ..coordinator import VirtualAmsCoordinator

SERVICE_REGISTER_SPOOL = "register_spool"
SERVICE_UPDATE_SPOOL = "update_spool"
SERVICE_REMOVE_SPOOL = "remove_spool"

_SCHEMA_REGISTER = vol.Schema(
    {
        vol.Optional(ATTR_FINGERPRINT): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_COLOR_HEX): cv.string,
        vol.Optional(ATTR_MATERIAL): cv.string,
        vol.Optional(ATTR_WEIGHT): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=9999)
        ),
        vol.Optional(ATTR_INITIAL_WEIGHT): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=9999)
        ),
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
    }
)

_SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional(ATTR_FINGERPRINT): cv.string,
        vol.Optional(ATTR_WEIGHT): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=9999)
        ),
        vol.Optional(ATTR_INITIAL_WEIGHT): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=9999)
        ),
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(ATTR_MATERIAL): cv.string,
    }
)

_SCHEMA_REMOVE = vol.Schema(
    {
        vol.Required(ATTR_FINGERPRINT): cv.string,
    }
)


def _get_coordinator(hass: HomeAssistant) -> VirtualAmsCoordinator:
    """Return the coordinator for the single Virtual AMS config entry."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        msg = "Virtual AMS is not configured"
        raise HomeAssistantError(msg)
    return entries[0].runtime_data.coordinator


async def async_setup_services(hass: HomeAssistant) -> None:
    """
    Register Virtual AMS service actions at component level.

    Called once from async_setup. Services are not removed during entry reload,
    satisfying the Silver Quality Scale requirement.
    """

    async def handle_register_spool(call: ServiceCall) -> None:
        await async_handle_register_spool(_get_coordinator(hass), call)

    async def handle_update_spool(call: ServiceCall) -> None:
        await async_handle_update_spool(_get_coordinator(hass), call)

    async def handle_remove_spool(call: ServiceCall) -> None:
        await async_handle_remove_spool(_get_coordinator(hass), call)

    if not hass.services.has_service(DOMAIN, SERVICE_REGISTER_SPOOL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REGISTER_SPOOL,
            handle_register_spool,
            schema=_SCHEMA_REGISTER,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_SPOOL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_UPDATE_SPOOL,
            handle_update_spool,
            schema=_SCHEMA_UPDATE,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REMOVE_SPOOL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_SPOOL,
            handle_remove_spool,
            schema=_SCHEMA_REMOVE,
        )

    LOGGER.debug("Services registered for %s", DOMAIN)
