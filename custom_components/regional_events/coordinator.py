"""DataUpdateCoordinator for Regional Events."""
from datetime import timedelta
import async_timeout
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER, DEFAULT_SCAN_INTERVAL, CITY_LIBEREC, CITY_JABLONEC
from .models import RegionalEvent
from .parsers.liberec import fetch_liberec_events
from .parsers.jablonec import fetch_jablonec_events
from .parsers.dfxs import fetch_dfxs_events
from .parsers.linserka import fetch_linserka_events
from .parsers.lipo_ink import fetch_lipo_events
from .parsers.zivy_liberec import fetch_zivy_liberec_events
from .engine.dedup import deduplicate_events
from .engine.enrichment import enrich_event
from .engine.scoring import score_event

class RegionalEventsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching regional events data."""

    def __init__(self, hass: HomeAssistant, cities: list[str], config_entry_id: str) -> None:
        """Initialize."""
        self.cities = cities
        self.config_entry_id = config_entry_id
        self.all_events = []  # Store all events for sensor access
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        session = async_get_clientsession(self.hass)
        all_events = []

        # Get user preferences from config entry
        config_entry = self.hass.config_entries.async_get_entry(self.config_entry_id)
        options = config_entry.options if config_entry else {}
        
        user_interests = options.get("interests", [])
        preferred_venues_raw = options.get("preferred_venues", [])
        if isinstance(preferred_venues_raw, str):
            preferred_venues = [v.strip() for v in preferred_venues_raw.split(",") if v.strip()]
        else:
            preferred_venues = preferred_venues_raw
            
        max_distance = options.get("max_distance", 25)
        blocked_categories = options.get("blocked_categories", [])

        try:
            async with async_timeout.timeout(30):
                events = []
                
                if CITY_LIBEREC in self.cities:
                    import asyncio
                    results = await asyncio.gather(
                        fetch_liberec_events(session),
                        fetch_dfxs_events(session),
                        fetch_linserka_events(session),
                        fetch_lipo_events(session),
                        fetch_zivy_liberec_events(session),
                        return_exceptions=True
                    )
                    for res in results:
                        if isinstance(res, list):
                            events.extend(res)
                        else:
                            LOGGER.error("Error in one of Liberec parsers: %s", res)
                
                if CITY_JABLONEC in self.cities:
                    jablonec_events = await fetch_jablonec_events(session)
                    events.extend(jablonec_events)
                
                # Deduplicate, enrich and score all events
                deduplicated = deduplicate_events(events)
                
                processed_events = []
                for event in deduplicated:
                    # Enrich with HA data (weather, distance)
                    enriched = enrich_event(event, self.hass)
                    
                    # Calculate score based on user interests
                    score_event(
                        enriched,
                        user_interests=user_interests,
                        preferred_venues=preferred_venues,
                        max_distance=max_distance,
                        blocked_categories=blocked_categories,
                    )
                    processed_events.append(enriched)
                
                all_events = processed_events
                
        except Exception as error:
            raise UpdateFailed(f"Error communicating with API: {error}") from error

        # Group by date for calendar storage
        data = {}
        for event in all_events:
            city = event.city
            if city not in data:
                data[city] = []
            data[city].append(event.to_calendar_dict())
        
        # Store all events flat for sensors and frontend
        self.all_events = all_events
        
        return {
            "cities": data,
            "all_events": [e.to_calendar_dict() for e in all_events]
        }
