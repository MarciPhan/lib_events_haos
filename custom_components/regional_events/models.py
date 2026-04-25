"""Data models for Regional Events integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
import hashlib
from typing import Optional


@dataclass
class RegionalEvent:
    """Represents a regional event."""

    uid: str
    title: str
    start: datetime | date
    end: Optional[datetime | date]
    location: Optional[str]
    city: str
    category: Optional[str]
    description: Optional[str]
    url: Optional[str]
    image_url: Optional[str]
    source: str
    
    # New fields for genius version
    price: Optional[str] = None
    is_free: Optional[bool] = None
    score: float = 0.0
    indoor_outdoor: Optional[str] = None  # "indoor", "outdoor", "unknown"
    lat: Optional[float] = None
    lon: Optional[float] = None
    distance_km: Optional[float] = None
    travel_time_min: Optional[int] = None
    weather_forecast: Optional[str] = None
    reasoning: Optional[list[str]] = None

    @staticmethod
    def generate_uid(title: str, start: date, location: Optional[str] = None) -> str:
        """Generate a unique identifier for an event."""
        uid_string = f"{title}:{start}:{location or 'unknown'}"
        return hashlib.sha256(uid_string.encode()).hexdigest()[:16]

    def to_calendar_dict(self) -> dict:
        """Convert to a dictionary format for calendar storage."""
        return {
            "uid": self.uid,
            "title": self.title,
            "start": self.start,
            "end": self.end,
            "location": self.location,
            "city": self.city,
            "category": self.category,
            "description": self.description,
            "url": self.url,
            "image_url": self.image_url,
            "source": self.source,
            "price": self.price,
            "is_free": self.is_free,
            "score": self.score,
            "indoor_outdoor": self.indoor_outdoor,
            "lat": self.lat,
            "lon": self.lon,
            "distance_km": self.distance_km,
            "travel_time_min": self.travel_time_min,
            "weather_forecast": self.weather_forecast,
            "reasoning": self.reasoning,
        }
