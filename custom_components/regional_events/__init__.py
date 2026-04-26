"""The Regional Events integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_CITIES
from .coordinator import RegionalEventsCoordinator

PLATFORMS: list[Platform] = [
    Platform.CALENDAR,
    Platform.SENSOR,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Regional Events from a config entry."""
    cities = entry.data.get(CONF_CITIES, [])
    coordinator = RegionalEventsCoordinator(hass, cities, entry.entry_id)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up services
    from .services import async_setup_services
    await async_setup_services(hass)

    # Register static path for frontend
    import os
    static_path = os.path.join(os.path.dirname(__file__), "frontend")
    hass.http.register_static_path("/regional_events_static", static_path)

    # Register Sidebar Panel
    if "frontend" in hass.config.components:
        hass.components.frontend.async_register_panel(
            component_name="custom",
            sidebar_title="Kulturní radar",
            sidebar_icon="mdi:radar",
            main_url="/regional_events_static/panel.js",
            panel_icon="mdi:radar",
            url_path="kulturni-radar",
            config={
                "entry_id": entry.entry_id,
                "title": "Kulturní radar Liberec & Jablonec"
            },
            require_admin=False
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
