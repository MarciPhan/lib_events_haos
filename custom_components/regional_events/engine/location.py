"""Location engine for distance and travel time calculation."""
import math
from homeassistant.core import HomeAssistant
from homeassistant.util.location import distance

def calculate_distance(hass: HomeAssistant, lat: float, lon: float) -> float | None:
    """Calculate distance from home coordinates in km."""
    home_lat = hass.config.latitude
    home_lon = hass.config.longitude
    
    if home_lat is None or home_lon is None:
        return None
        
    return distance(home_lat, home_lon, lat, lon) / 1000.0

def estimate_travel_time(distance_km: float) -> int:
    """Estimate travel time in minutes (very simple approximation)."""
    # Assuming average speed in city + overhead
    if distance_km < 2:
        return 10  # Minimum overhead
    
    # Approx 30 km/h average
    return int((distance_km / 30.0) * 60.0) + 5
