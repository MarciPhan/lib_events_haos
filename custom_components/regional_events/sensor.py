"""Support for Regional Events sensors."""
from __future__ import annotations

from datetime import datetime, timedelta, date

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RegionalEventsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Regional Events sensor platform."""
    coordinator: RegionalEventsCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = [
        # Count sensors
        EventsCountSensor(coordinator, "today", "Akce dnes"),
        EventsCountSensor(coordinator, "tomorrow", "Akce zítra"),
        EventsCountSensor(coordinator, "weekend", "Akce o víkendu"),
        EventsCountSensor(coordinator, "week", "Akce tento týden"),
        EventsCountSensor(coordinator, "free", "Akce zdarma"),
        EventsCountSensor(coordinator, "kids", "Akce pro děti"),
        
        # Detail sensors
        NextEventSensor(coordinator, "Nejbližší akce"),
        RecommendedEventSensor(coordinator, "today", "Doporučená akce dnes"),
        RecommendedEventSensor(coordinator, "weekend", "Doporučená akce o víkendu"),
    ]
    
    async_add_entities(sensors)


class EventsCountSensor(CoordinatorEntity[RegionalEventsCoordinator], SensorEntity):
    """Sensor for counting events in a time period or category."""

    def __init__(
        self,
        coordinator: RegionalEventsCoordinator,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry_id}_count_{sensor_type}"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the count of events."""
        events = self.coordinator.all_events
        if not events:
            return 0
        
        today = datetime.now().date()
        count = 0
        
        for event in events:
            e_date = event.start.date() if hasattr(event.start, 'date') else event.start
            
            if self._type == "today":
                if e_date == today: count += 1
            elif self._type == "tomorrow":
                if e_date == today + timedelta(days=1): count += 1
            elif self._type == "weekend":
                if e_date.weekday() in [5, 6] and 0 <= (e_date - today).days <= 7: count += 1
            elif self._type == "week":
                if 0 <= (e_date - today).days <= 7: count += 1
            elif self._type == "free":
                if event.is_free: count += 1
            elif self._type == "kids":
                if event.category == "kids" or (event.description and "děti" in event.description.lower()):
                    count += 1
        
        return count


class NextEventSensor(CoordinatorEntity[RegionalEventsCoordinator], SensorEntity):
    """Sensor for the next upcoming event."""

    def __init__(self, coordinator: RegionalEventsCoordinator, name: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry_id}_next_event"

    @property
    def native_value(self) -> str | None:
        """Return next event title."""
        events = self.coordinator.all_events
        if not events: return None
        
        now = datetime.now()
        upcoming = [e for e in events if (e.start if isinstance(e.start, datetime) else datetime.combine(e.start, datetime.min.time())) >= now]
        if not upcoming: return None
        
        upcoming.sort(key=lambda e: e.start)
        return upcoming[0].title

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        events = self.coordinator.all_events
        now = datetime.now()
        upcoming = [e for e in events if (e.start if isinstance(e.start, datetime) else datetime.combine(e.start, datetime.min.time())) >= now]
        
        attrs = {
            "all_events": self.coordinator.data.get("all_events", [])
        }
        
        if not upcoming: return attrs
        
        upcoming.sort(key=lambda e: e.start)
        event = upcoming[0]
        
        attrs.update({
            "start": event.start.isoformat() if hasattr(event.start, 'isoformat') else str(event.start),
            "location": event.location,
            "category": event.category,
            "score": event.score,
            "distance_km": event.distance_km,
            "travel_time_min": event.travel_time_min,
            "weather": event.weather_forecast,
            "is_free": event.is_free,
            "price": event.price,
            "url": event.url,
            "reasoning": event.reasoning,
        })
        return attrs


class RecommendedEventSensor(CoordinatorEntity[RegionalEventsCoordinator], SensorEntity):
    """Sensor for top recommended event for a period."""

    def __init__(self, coordinator: RegionalEventsCoordinator, period: str, name: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._period = period
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry_id}_rec_{period}"

    @property
    def native_value(self) -> str | None:
        """Return recommended event title."""
        event = self._get_best_event()
        return event.title if event else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        event = self._get_best_event()
        if not event: return {}
        
        return {
            "score": event.score,
            "reasoning": event.reasoning,
            "start": event.start.isoformat() if hasattr(event.start, 'isoformat') else str(event.start),
            "location": event.location,
            "distance_km": event.distance_km,
            "weather": event.weather_forecast,
            "price": event.price,
            "url": event.url,
            "image": event.image_url,
        }

    def _get_best_event(self):
        """Find best event for period."""
        events = self.coordinator.all_events
        if not events: return None
        
        today = datetime.now().date()
        filtered = []
        
        for event in events:
            e_date = event.start.date() if hasattr(event.start, 'date') else event.start
            if self._period == "today" and e_date == today:
                filtered.append(event)
            elif self._period == "weekend" and e_date.weekday() in [5, 6] and 0 <= (e_date - today).days <= 7:
                filtered.append(event)
        
        if not filtered: return None
        filtered.sort(key=lambda x: x.score, reverse=True)
        return filtered[0]
