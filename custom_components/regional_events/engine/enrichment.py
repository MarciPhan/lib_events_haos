"""Event enrichment engine."""
from datetime import datetime
from typing import Optional

from homeassistant.core import HomeAssistant

from ..models import RegionalEvent
from .venues import get_venue_info
from .categories import normalize_category
from .weather import get_weather_forecast, is_outdoor_friendly
from .location import calculate_distance, estimate_travel_time


def enrich_event(event: RegionalEvent, hass: HomeAssistant = None) -> RegionalEvent:
    """Enrich event with additional data."""
    
    # Normalize category
    if event.category:
        normalized_cat = normalize_category(event.category)
        if normalized_cat != event.category:
            event.category = normalized_cat
    
    # Enrich venue information
    if event.location:
        venue_info = get_venue_info(event.location)
        if venue_info:
            if not event.description and venue_info.get("description"):
                event.description = venue_info.get("description")
            
            # Enrich GPS and tags
            if not event.lat:
                event.lat = venue_info.get("lat")
            if not event.lon:
                event.lon = venue_info.get("lon")
            
            # Detect indoor/outdoor from tags
            tags = venue_info.get("tags", [])
            if "indoor" in tags:
                event.indoor_outdoor = "indoor"
            elif "outdoor" in tags:
                event.indoor_outdoor = "outdoor"
    
    # Enrich with HA data if available
    if hass:
        # Distance and travel time
        if event.lat and event.lon:
            event.distance_km = calculate_distance(hass, event.lat, event.lon)
            if event.distance_km:
                event.travel_time_min = estimate_travel_time(event.distance_km)
        
        # Weather
        if isinstance(event.start, datetime):
            forecast = get_weather_forecast(hass, event.start)
            if forecast:
                condition = forecast.get("condition")
                event.weather_forecast = condition
                
                # If outdoor, check if weather is okay
                if event.indoor_outdoor == "outdoor" and condition:
                    if not is_outdoor_friendly(condition):
                        if not event.reasoning:
                            event.reasoning = []
                        event.reasoning.append(f"Pozor: Akce je venku a očekává se {condition}")
    
    # Price parsing (simple version)
    if event.description:
        desc_lower = event.description.lower()
        if "zdarma" in desc_lower or "vstup volný" in desc_lower:
            event.is_free = True
            event.price = "Zdarma"
        elif "kč" in desc_lower:
            # Try to find price like "120 Kč"
            import re
            match = re.search(r"(\d+)\s*kč", desc_lower)
            if match:
                event.price = f"{match.group(1)} Kč"
                event.is_free = False
    
    return event
