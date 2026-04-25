"""Options flow for Regional Events integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Regional Events."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        return await self.async_step_preferences()

    async def async_step_preferences(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle preferences step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="preferences",
            data_schema=vol.Schema({
                vol.Optional(
                    "interests",
                    default=self.config_entry.options.get("interests", [])
                ): cv.multi_select({
                    "music": "🎵 Hudba",
                    "theatre": "🎭 Divadlo",
                    "cinema": "🎬 Kino",
                    "exhibition": "🖼️ Výstava",
                    "education": "📚 Vzdělání",
                    "kids": "👶 Děti",
                    "sports": "⚽ Sport",
                    "business": "💼 Podnikání",
                    "market": "🛍️ Trhy",
                    "food": "🍽️ Gastronomie",
                    "technologie": "💻 Technologie",
                }),
                vol.Optional(
                    "blocked_categories",
                    default=self.config_entry.options.get("blocked_categories", [])
                ): cv.multi_select({
                    "music": "🎵 Hudba",
                    "theatre": "🎭 Divadlo",
                    "cinema": "🎬 Kino",
                    "exhibition": "🖼️ Výstava",
                    "education": "📚 Vzdělání",
                    "kids": "👶 Děti",
                    "sports": "⚽ Sport",
                    "business": "💼 Podnikání",
                    "market": "🛍️ Trhy",
                    "food": "🍽️ Gastronomie",
                }),
                vol.Optional(
                    "preferred_venues",
                    default=self.config_entry.options.get("preferred_venues", ["Linserka", "Lipo.ink"])
                ): cv.string,
                vol.Optional(
                    "max_distance",
                    default=self.config_entry.options.get("max_distance", 25)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                vol.Optional(
                    "enable_notifications",
                    default=self.config_entry.options.get("enable_notifications", True)
                ): cv.boolean,
            }),
        )
