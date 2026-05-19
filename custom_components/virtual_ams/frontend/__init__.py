"""Lovelace card registration for Virtual AMS."""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig
from homeassistant.helpers.event import async_call_later

from ..const import CARD_FILENAME, CARD_URL_BASE, CARD_VERSION, DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_CARD_URL = f"{CARD_URL_BASE}/{CARD_FILENAME}"
_CARD_URL_VERSIONED = f"{_CARD_URL}?v={CARD_VERSION}"
_CARD_PATH = pathlib.Path(__file__).parent / CARD_FILENAME


class VirtualAmsCardRegistration:
    """
    Register the Virtual AMS Lovelace card as a static HTTP path.

    In storage mode it also registers the card as a Lovelace resource so
    users don't need to add the resource URL manually.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize with the HomeAssistant instance."""
        self.hass = hass

    @property
    def _lovelace(self) -> object | None:
        return self.hass.data.get("lovelace")

    @property
    def lovelace_resource_mode(self) -> str | None:
        """Return the current Lovelace resource mode, or None if unavailable."""
        lovelace = self._lovelace
        if lovelace is None:
            return None
        for attr in ("resource_mode", "mode"):
            if hasattr(lovelace, attr):
                return getattr(lovelace, attr)
        if isinstance(lovelace, dict):
            return lovelace.get("mode")
        return None

    @property
    def lovelace_resources(self) -> object | None:
        """Return the Lovelace resources store, or None if unavailable."""
        lovelace = self._lovelace
        if lovelace is None:
            return None
        if hasattr(lovelace, "resources"):
            return lovelace.resources
        if isinstance(lovelace, dict):
            return lovelace.get("resources")
        return None

    async def async_register(self) -> None:
        """Register the static HTTP path and, if possible, the Lovelace resource."""
        await self._async_register_static_path()
        if self.lovelace_resource_mode == "storage":
            await self._async_wait_for_lovelace_resources()

    async def async_unregister(self) -> None:
        """Remove the Lovelace resource (storage mode only)."""
        if self.lovelace_resource_mode != "storage":
            return
        resources = self.lovelace_resources
        if resources is None:
            return
        for res in resources.async_items():
            if res["url"].startswith(_CARD_URL):
                await resources.async_delete_item(res["id"])
                LOGGER.debug("Removed Lovelace resource %s", res["url"])

    async def _async_register_static_path(self) -> None:
        """Register /virtual_ams/virtual-ams-card.js as a static HTTP path."""
        if not _CARD_PATH.exists():
            LOGGER.warning("Card file not found: %s", _CARD_PATH)
            return
        # Guard: only register once per HA instance, not once per config entry.
        if f"{DOMAIN}_card_path" in self.hass.data:
            return
        try:
            await self.hass.http.async_register_static_paths(
                [StaticPathConfig(_CARD_URL, str(_CARD_PATH), cache_headers=False)]
            )
            self.hass.data[f"{DOMAIN}_card_path"] = True
            LOGGER.debug("Registered static path %s -> %s", _CARD_URL, _CARD_PATH)
        except RuntimeError:
            LOGGER.debug("Static path %s already registered", _CARD_URL)

    async def _async_wait_for_lovelace_resources(self) -> None:
        """Wait until Lovelace resources are loaded, then register the card."""

        async def _try(_now: object) -> None:
            resources = self.lovelace_resources
            if resources is None or not resources.loaded:
                LOGGER.debug("Lovelace resources not ready, retrying in 5 s")
                async_call_later(self.hass, 5, _try)
                return
            await self._async_register_lovelace_resource(resources)

        await _try(None)

    async def _async_register_lovelace_resource(self, resources: object) -> None:
        """Add or update the card URL in Lovelace resources."""
        for res in resources.async_items():
            if res["url"].split("?")[0] == _CARD_URL:
                if res["url"] == _CARD_URL_VERSIONED:
                    LOGGER.debug(
                        "Lovelace resource already up to date (%s)", CARD_VERSION
                    )
                else:
                    await resources.async_update_item(
                        res["id"],
                        {"res_type": "module", "url": _CARD_URL_VERSIONED},
                    )
                    LOGGER.debug("Updated Lovelace resource to %s", _CARD_URL_VERSIONED)
                return

        await resources.async_create_item(
            {"res_type": "module", "url": _CARD_URL_VERSIONED}
        )
        LOGGER.debug("Registered Lovelace resource %s", _CARD_URL_VERSIONED)
