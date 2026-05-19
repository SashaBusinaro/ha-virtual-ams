"""Config flow for virtual_ams."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_PRINT_STATE_SENSOR,
    CONF_PRINT_WEIGHT_SENSOR,
    CONF_SPOOL_SENSOR,
    DOMAIN,
)


def _user_schema(user_input: dict | None = None) -> vol.Schema:
    """Build the form schema, pre-filling with existing values."""
    defaults = user_input or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_SPOOL_SENSOR, default=defaults.get(CONF_SPOOL_SENSOR)
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                CONF_PRINT_STATE_SENSOR, default=defaults.get(CONF_PRINT_STATE_SENSOR)
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                CONF_PRINT_WEIGHT_SENSOR,
                default=defaults.get(CONF_PRINT_WEIGHT_SENSOR),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        }
    )


class VirtualAmsConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Virtual AMS."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Virtual AMS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a reconfiguration flow initialized by the user."""
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            return self.async_update_reload_and_abort(entry, data=user_input)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_user_schema(dict(entry.data)),
        )
