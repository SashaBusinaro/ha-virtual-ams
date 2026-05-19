"""Event-driven coordinator for Virtual AMS inventory management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from ..const import (
    ATTR_COLOR_HEX,
    ATTR_DISPLAY_NAME,
    ATTR_FINGERPRINT,
    ATTR_FRIENDLY_COLOR,
    ATTR_FRIENDLY_NAME,
    ATTR_IN_INVENTORY,
    ATTR_INITIAL_WEIGHT,
    ATTR_LAST_USED,
    ATTR_MATERIAL,
    ATTR_NAME,
    ATTR_WEIGHT,
    COLOR_MAP,
    CONF_PRINT_STATE_SENSOR,
    CONF_PRINT_WEIGHT_SENSOR,
    CONF_SPOOL_SENSOR,
    DOMAIN,
    LOGGER,
    PRINT_STATE_IDLE,
    PRINT_STATE_PRINTING,
)
from ..store import VirtualAmsStore

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry

    from ..data import SpoolRegistrationData


def _normalize_color(raw: str) -> str:
    """Normalize a color value to uppercase #RRGGBBAA format."""
    color = raw.strip().upper()
    if not color.startswith("#"):
        color = "#" + color
    return color


class VirtualAmsCoordinator:
    """Manages the filament inventory and listens to printer state changes."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self._config_entry = config_entry
        self._store = VirtualAmsStore(hass)
        self.inventory: dict[str, dict] = {}
        self._unsub_listeners: list[Callable] = []

    @property
    def entry_id(self) -> str:
        """Return the config entry ID."""
        return self._config_entry.entry_id

    @property
    def signal(self) -> str:
        """Return the dispatcher signal for this entry."""
        return f"{DOMAIN}_{self._config_entry.entry_id}_update"

    @property
    def spool_sensor(self) -> str:
        """Return the spool sensor entity ID."""
        return self._config_entry.data[CONF_SPOOL_SENSOR]

    @property
    def print_state_sensor(self) -> str:
        """Return the print state sensor entity ID."""
        return self._config_entry.data[CONF_PRINT_STATE_SENSOR]

    @property
    def print_weight_sensor(self) -> str:
        """Return the print weight sensor entity ID."""
        return self._config_entry.data[CONF_PRINT_WEIGHT_SENSOR]

    async def async_setup(self) -> None:
        """Load inventory and subscribe to sensor state changes."""
        self.inventory = await self._store.async_load()
        self._unsub_listeners.extend(
            [
                async_track_state_change_event(
                    self.hass, [self.print_state_sensor], self._handle_print_state
                ),
                async_track_state_change_event(
                    self.hass, [self.spool_sensor], self._handle_spool_change
                ),
            ]
        )

    def teardown(self) -> None:
        """Unsubscribe all state-change listeners."""
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()

    @callback
    def _handle_spool_change(self, _event: object) -> None:
        async_dispatcher_send(self.hass, self.signal)

    @callback
    def _handle_print_state(self, event: object) -> None:
        old = event.data.get("old_state")
        new = event.data.get("new_state")
        if (
            old
            and new
            and old.state == PRINT_STATE_PRINTING
            and new.state == PRINT_STATE_IDLE
        ):
            self.hass.async_create_task(self._auto_deduct())

    async def _auto_deduct(self) -> None:
        weight_state = self.hass.states.get(self.print_weight_sensor)
        if not weight_state:
            return
        try:
            weight = float(weight_state.state)
        except ValueError, TypeError:
            return
        if weight <= 0:
            return

        fingerprint = self.get_current_fingerprint()
        if not fingerprint or fingerprint not in self.inventory:
            LOGGER.info(
                "Spool %s not in inventory, skipping auto-deduction", fingerprint
            )
            return

        current = self.inventory[fingerprint]
        new_spool = {
            **current,
            ATTR_WEIGHT: round(max(0.0, current[ATTR_WEIGHT] - weight), 1),
            ATTR_LAST_USED: dt_util.now().isoformat(),
        }
        self.inventory = {**self.inventory, fingerprint: new_spool}
        await self._store.async_save(self.inventory)
        LOGGER.debug(
            "Auto-deducted %.1fg from %s (remaining: %.1fg)",
            weight,
            fingerprint,
            new_spool[ATTR_WEIGHT],
        )
        async_dispatcher_send(self.hass, self.signal)

    def get_current_fingerprint(self) -> str | None:
        """Return the fingerprint of the currently loaded spool, or None."""
        state = self.hass.states.get(self.spool_sensor)
        if not state:
            return None
        name = state.attributes.get("name", "")
        if not name:
            return None
        color = state.attributes.get("color", "") or "00000000"
        return f"{name}_{_normalize_color(color)}"

    def get_active_spool(self) -> dict | None:
        """Return a dict describing the currently loaded spool, or None."""
        state = self.hass.states.get(self.spool_sensor)
        if not state:
            return None
        name = state.attributes.get("name", "")
        if not name:
            return None
        color = state.attributes.get("color", "")
        color_hex = _normalize_color(color) if color else "#00000000"
        fingerprint = f"{name}_{color_hex}"
        friendly_color = COLOR_MAP.get(color_hex, color_hex)
        spool_data = self.inventory.get(fingerprint, {})
        display_name = spool_data.get(ATTR_FRIENDLY_NAME, f"{name} {friendly_color}")
        return {
            ATTR_FINGERPRINT: fingerprint,
            ATTR_NAME: name,
            ATTR_COLOR_HEX: color_hex,
            ATTR_FRIENDLY_COLOR: friendly_color,
            # Use display_name instead of friendly_name to avoid collision
            # with HA's auto-injected entity friendly_name attribute.
            ATTR_DISPLAY_NAME: display_name,
            ATTR_MATERIAL: spool_data.get(
                ATTR_MATERIAL, state.attributes.get("type", "")
            ),
            ATTR_WEIGHT: spool_data.get(ATTR_WEIGHT, 0),
            ATTR_INITIAL_WEIGHT: spool_data.get(ATTR_INITIAL_WEIGHT, 0),
            ATTR_IN_INVENTORY: fingerprint in self.inventory,
            ATTR_LAST_USED: spool_data.get(ATTR_LAST_USED),
        }

    async def register_spool(self, data: SpoolRegistrationData) -> None:
        """Add or replace a spool in the inventory."""
        color_hex = _normalize_color(data.color_hex)
        friendly_color = COLOR_MAP.get(color_hex, color_hex)
        existing = self.inventory.get(data.fingerprint, {})
        new_spool = {
            ATTR_FINGERPRINT: data.fingerprint,
            ATTR_NAME: data.name,
            ATTR_COLOR_HEX: color_hex,
            ATTR_FRIENDLY_COLOR: friendly_color,
            ATTR_FRIENDLY_NAME: data.friendly_name or f"{data.name} {friendly_color}",
            ATTR_MATERIAL: data.material,
            ATTR_WEIGHT: round(data.weight, 1),
            ATTR_INITIAL_WEIGHT: round(
                data.initial_weight if data.initial_weight is not None else 1000.0,
                1,
            ),
            ATTR_LAST_USED: existing.get(ATTR_LAST_USED),
        }
        self.inventory = {**self.inventory, data.fingerprint: new_spool}
        await self._store.async_save(self.inventory)
        async_dispatcher_send(self.hass, self.signal)

    async def update_spool(self, fingerprint: str, **kwargs: object) -> None:
        """Update specific fields of an existing spool."""
        if fingerprint not in self.inventory:
            msg = f"Spool '{fingerprint}' not found in inventory"
            raise ValueError(msg)
        updates = {
            key: kwargs[key]
            for key in (
                ATTR_WEIGHT,
                ATTR_INITIAL_WEIGHT,
                ATTR_FRIENDLY_NAME,
                ATTR_MATERIAL,
            )
            if key in kwargs
        }
        if not updates:
            return
        new_spool = {**self.inventory[fingerprint], **updates}
        self.inventory = {**self.inventory, fingerprint: new_spool}
        await self._store.async_save(self.inventory)
        async_dispatcher_send(self.hass, self.signal)

    async def remove_spool(self, fingerprint: str) -> None:
        """Remove a spool from the inventory."""
        if fingerprint not in self.inventory:
            return
        self.inventory = {k: v for k, v in self.inventory.items() if k != fingerprint}
        await self._store.async_save(self.inventory)
        async_dispatcher_send(self.hass, self.signal)
