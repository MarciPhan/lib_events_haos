"""Support for Regional Events calendar."""
from __future__ import annotations

from datetime import datetime, timedelta, date

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CITY_LIBEREC, CITY_JABLONEC
from .coordinator import RegionalEventsCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Regional Events calendar platform."""
    coordinator: RegionalEventsCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    if CITY_LIBEREC in coordinator.cities:
        entities.append(RegionalCalendarEntity(coordinator, CITY_LIBEREC, "Akce Liberec"))
    if CITY_JABLONEC in coordinator.cities:
        entities.append(RegionalCalendarEntity(coordinator, CITY_JABLONEC, "Akce Jablonec"))
        
    async_add_entities(entities)

class RegionalCalendarEntity(CoordinatorEntity[RegionalEventsCoordinator], CalendarEntity):
    """A calendar entity for regional events."""

    def __init__(
        self,
        coordinator: RegionalEventsCoordinator,
        city: str,
        name: str,
    ) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self._city = city
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry_id}_{city}"
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self.coordinator.data.get("cities", {}).get(self._city, [])
        if not events:
            return None
        
        # Sort by start date and filter past events
        now = datetime.now().date()
        upcoming = [e for e in events if (isinstance(e["start"], datetime) and e["start"].date() >= now) or (isinstance(e["start"], date) and not isinstance(e["start"], datetime) and e["start"] >= now)]
        upcoming.sort(key=lambda x: x["start"] if isinstance(x["start"], date) and not isinstance(x["start"], datetime) else x["start"].date())
        
        if not upcoming:
            return None
            
        next_event = upcoming[0]
        start = next_event["start"]
        end = next_event.get("end")
        
        # Ensure datetime objects
        if isinstance(start, date) and not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time())
        if end and isinstance(end, date) and not isinstance(end, datetime):
            end = datetime.combine(end, datetime.min.time())
        elif end is None:
            end = start
        
        return CalendarEvent(
            summary=next_event["title"],
            start=start,
            end=end,
            location=next_event.get("location"),
            description=next_event.get("description"),
            uid=next_event["uid"],
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = self.coordinator.data.get("cities", {}).get(self._city, [])
        if not events:
            return []
        
        result = []
        for event in events:
            event_start = event["start"]
            event_end = event.get("end")
            
            # Convert date to datetime if needed
            if isinstance(event_start, date) and not isinstance(event_start, datetime):
                event_start = datetime.combine(event_start, datetime.min.time())
            if event_end and isinstance(event_end, date) and not isinstance(event_end, datetime):
                event_end = datetime.combine(event_end, datetime.min.time())
            elif event_end is None:
                event_end = event_start
            
            # Check if event falls within range
            if start_date.date() <= event_start.date() <= end_date.date():
                description = event.get("description", "")
                if event.get("url"):
                    description = f"{description}\n\nVíce na: {event['url']}".strip()
                
                result.append(
                    CalendarEvent(
                        summary=event["title"],
                        start=event_start,
                        end=event_end,
                        location=event.get("location"),
                        description=description or None,
                        uid=event["uid"],
                    )
                )
        return result
