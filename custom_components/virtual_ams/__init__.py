"""Virtual AMS - filament inventory manager for Bambulab printers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import VirtualAmsCoordinator
from .data import VirtualAmsData
from .frontend import VirtualAmsCardRegistration
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import VirtualAmsConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    """Register Virtual AMS service actions (called once at component load)."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: VirtualAmsConfigEntry) -> bool:
    """Set up a Virtual AMS config entry."""
    coordinator = VirtualAmsCoordinator(hass, entry)
    await coordinator.async_setup()
    entry.runtime_data = VirtualAmsData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    cards = VirtualAmsCardRegistration(hass)
    await cards.async_register()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: VirtualAmsConfigEntry) -> bool:
    """Unload a Virtual AMS config entry."""
    entry.runtime_data.coordinator.teardown()

    cards = VirtualAmsCardRegistration(hass)
    await cards.async_unregister()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: VirtualAmsConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
