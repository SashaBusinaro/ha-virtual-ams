"""Persistent storage for Virtual AMS inventory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class VirtualAmsStore:
    """Thin wrapper around HA's Store for spool inventory persistence."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the store."""
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY, private=True)

    async def async_load(self) -> dict:
        """Load the spool inventory from persistent storage."""
        data = await self._store.async_load()
        return (data or {}).get("spools", {})

    async def async_save(self, spools: dict) -> None:
        """Persist the spool inventory to storage."""
        await self._store.async_save({"spools": spools})
