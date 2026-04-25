"""Scoring engine for events."""
from datetime import datetime, timedelta
from typing import Optional

from ..models import RegionalEvent
from ..const import LOGGER


def score_event(
    event: RegionalEvent,
    user_interests: Optional[list[str]] = None,
    preferred_venues: Optional[list[str]] = None,
    max_distance: Optional[float] = None,
    blocked_categories: Optional[list[str]] = None,
) -> float:
    """Calculate event score 0-100 for recommendations."""
    score = 50.0  # Base score
    reasoning = []
    
    user_interests = user_interests or []
    preferred_venues = preferred_venues or []
    blocked_categories = blocked_categories or []
    
    # Category match
    if event.category:
        if event.category.lower() in [i.lower() for i in blocked_categories]:
            event.reasoning = ["Blokovaná kategorie"]
            return 0.0
        
        if event.category.lower() in [i.lower() for i in user_interests]:
            score += 25
            reasoning.append(f"Zajímavá kategorie: {event.category}")
    
    # Venue preference
    if event.location:
        if any(v.lower() in event.location.lower() for v in preferred_venues):
            score += 20
            reasoning.append("Oblíbené místo")
    
    # Distance
    if event.distance_km is not None:
        if max_distance and event.distance_km > max_distance:
            score -= 30
            reasoning.append(f"Moc daleko ({event.distance_km:.1f} km)")
        elif event.distance_km < 5:
            score += 15
            reasoning.append("Velmi blízko")
        elif event.distance_km < 15:
            score += 5
            reasoning.append("Poblíž")
    
    # Free vs paid
    if event.is_free:
        score += 15
        reasoning.append("Akce zdarma")
    
    # Weather consideration
    if event.weather_forecast:
        from .weather import is_outdoor_friendly
        is_ok = is_outdoor_friendly(event.weather_forecast)
        
        if event.indoor_outdoor == "outdoor":
            if not is_ok:
                score -= 40
                reasoning.append(f"Špatné počasí pro venkovní akci ({event.weather_forecast})")
            else:
                score += 5
                reasoning.append("Dobré počasí pro venkovní akci")
        elif event.indoor_outdoor == "indoor" and not is_ok:
            score += 10
            reasoning.append("Ideální úkryt před špatným počasím")
    
    # Time of day preference
    if hasattr(event.start, 'hour'):
        if 18 <= event.start.hour <= 21:  # Prime time
            score += 10
    
    # Kids-friendly
    if event.category == "kids" or (event.description and "děti" in event.description.lower()):
        score += 10
    
    # Save reasoning and score
    event.reasoning = reasoning
    event.score = max(0, min(100, score))
    return event.score


def get_top_events(
    events: list[RegionalEvent],
    count: int = 3,
    min_score: float = 60,
    **scoring_kwargs
) -> list[tuple[RegionalEvent, float]]:
    """Get top scored events."""
    scored = []
    
    for event in events:
        score = score_event(event, **scoring_kwargs)
        if score >= min_score:
            scored.append((event, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return scored[:count]
