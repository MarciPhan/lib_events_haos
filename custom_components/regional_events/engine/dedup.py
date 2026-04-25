"""Deduplication engine for events."""
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional

from ..models import RegionalEvent
from ..const import LOGGER


def deduplicate_events(events: list[RegionalEvent]) -> list[RegionalEvent]:
    """Deduplicate events by similarity."""
    if not events:
        return events
    
    # Group by date first
    by_date = {}
    for event in events:
        date_key = event.start.date() if hasattr(event.start, 'date') else event.start
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(event)
    
    result = []
    processed_uids = set()
    
    for date_events in by_date.values():
        # Sort by reliability (source)
        date_events.sort(key=lambda e: source_reliability(e.source), reverse=True)
        
        for event in date_events:
            if event.uid in processed_uids:
                continue
            
            # Find duplicates
            duplicates = find_similar_events(event, date_events, processed_uids)
            
            # Merge similar events and keep best one
            merged = merge_events([event] + duplicates)
            result.append(merged)
            
            # Mark all as processed
            for dup in duplicates:
                processed_uids.add(dup.uid)
            processed_uids.add(event.uid)
    
    return result


def find_similar_events(
    event: RegionalEvent,
    candidates: list[RegionalEvent],
    processed_uids: set[str]
) -> list[RegionalEvent]:
    """Find similar events to merge."""
    similar = []
    
    for candidate in candidates:
        if candidate.uid == event.uid or candidate.uid in processed_uids:
            continue
        
        # Check similarity
        title_sim = string_similarity(event.title, candidate.title)
        location_sim = 1.0 if (event.location or "").lower() == (candidate.location or "").lower() else 0.0
        
        # Must have high title similarity and same/similar location
        if title_sim > 0.82 and location_sim > 0.5:
            similar.append(candidate)
    
    return similar


def merge_events(events: list[RegionalEvent]) -> RegionalEvent:
    """Merge duplicate events, keeping best information."""
    if not events:
        raise ValueError("Cannot merge empty list")
    
    if len(events) == 1:
        return events[0]
    
    # Sort by reliability
    events.sort(key=lambda e: source_reliability(e.source), reverse=True)
    
    best = events[0]
    
    # Use best available description
    description = best.description
    for event in events:
        if event.description and (not description or len(event.description) > len(description)):
            description = event.description
    
    # Use best available image
    image_url = best.image_url
    for event in events:
        if event.image_url and not image_url:
            image_url = event.image_url
    
    # Combine categories
    categories = set()
    if best.category:
        categories.add(best.category)
    for event in events:
        if event.category:
            categories.add(event.category)
    category = list(categories)[0] if categories else best.category
    
    # Return merged event
    merged = RegionalEvent(
        uid=best.uid,
        title=best.title,
        start=best.start,
        end=best.end or events[1].end if len(events) > 1 else best.end,
        location=best.location,
        city=best.city,
        category=category,
        description=description,
        url=best.url,
        image_url=image_url,
        source=best.source
    )
    
    LOGGER.debug(f"Merged {len(events)} events into {merged.uid}")
    return merged


def string_similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    return SequenceMatcher(None, a, b).ratio()


def source_reliability(source: str) -> float:
    """Return reliability score for a source."""
    reliability_map = {
        "365jablonec.cz": 0.95,
        "visitliberec.eu": 0.90,
        "dfxs.cz": 0.90,
        "mestojablonec.cz": 0.85,
        "kraj-lbc.cz": 0.75,
    }
    return reliability_map.get(source, 0.50)
