"""Config flow for Regional Events integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_CITIES, CITY_LIBEREC, CITY_JABLONEC
from .options_flow import OptionsFlow

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CITIES, default=[CITY_LIBEREC, CITY_JABLONEC]): cv.multi_select(
            {
                CITY_LIBEREC: "Liberec",
                CITY_JABLONEC: "Jablonec nad Nisou",
            }
        ),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Regional Events."""

    VERSION = 1
    options_flow_handler = OptionsFlow

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Kulturní radar",
            data=user_input,
            options={
                "preferred_categories": [],
                "blocked_categories": [],
                "enable_notifications": True,
                "prefer_free_events": False,
            }
        )
