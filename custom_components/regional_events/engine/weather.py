"""Weather engine for event suitability assessment."""
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.components.weather import (
    ATTR_FORECAST,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TIME,
)

def get_weather_forecast(hass: HomeAssistant, event_time: datetime) -> dict | None:
    """Get weather forecast for a specific event time."""
    # Find first weather entity
    weather_entities = hass.states.async_entity_ids("weather")
    if not weather_entities:
        return None
        
    weather_state = hass.states.get(weather_entities[0])
    if not weather_state:
        return None
        
    forecast = weather_state.attributes.get(ATTR_FORECAST)
    if not forecast:
        return None
        
    # Find closest forecast
    closest_forecast = None
    min_diff = None
    
    for f in forecast:
        f_time = datetime.fromisoformat(f[ATTR_FORECAST_TIME].replace("Z", "+00:00"))
        # Make event_time offset-aware if needed
        if event_time.tzinfo is None and f_time.tzinfo is not None:
            # Fallback if tzinfo missing
            diff = abs((f_time.replace(tzinfo=None) - event_time).total_seconds())
        else:
            diff = abs((f_time - event_time).total_seconds())
            
        if min_diff is None or diff < min_diff:
            min_diff = diff
            closest_forecast = f
            
    # Only return if forecast is within 12 hours of event
    if min_diff and min_diff > 12 * 3600:
        return None
        
    return closest_forecast

def is_outdoor_friendly(condition: str) -> bool:
    """Assess if weather condition is suitable for outdoor events."""
    bad_conditions = ["rainy", "snowy", "lightning", "hail", "pouring"]
    return condition not in bad_conditions
