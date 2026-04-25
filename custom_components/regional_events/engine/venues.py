"""Venue database and location information."""

VENUES = {
    "linserka": {
        "name": "Linserka",
        "city": "Liberec",
        "address": "Husova 12, Liberec",
        "lat": 50.7636,
        "lon": 15.0491,
        "tags": ["kultura", "komunita", "technologie", "indoor"],
        "description": "Komunitní prostor a galerie v Liberci",
    },
    "lipo.ink": {
        "name": "Lipo.ink",
        "city": "Liberec",
        "address": "Okružní 44, Liberec",
        "lat": 50.7734,
        "lon": 15.0365,
        "tags": ["podnikání", "vzdělávání", "komunita"],
        "description": "Coworking space a vzdělávací centrum",
    },
    "dfxš": {
        "name": "Divadlo F. X. Šaldy",
        "city": "Liberec",
        "address": "Lidická 14, Liberec",
        "lat": 50.7704,
        "lon": 15.0423,
        "tags": ["divadlo", "kultura"],
        "description": "Hlavní divadlo v Liberci",
    },
    "eurocentrum": {
        "name": "Eurocentrum Jablonec",
        "city": "Jablonec nad Nisou",
        "address": "Mírová 1285, Jablonec",
        "lat": 50.8656,
        "lon": 15.1727,
        "tags": ["nákupy", "zábava"],
        "description": "Obchodní a zábavní centrum",
    },
}


def get_venue_info(venue_name: str) -> dict | None:
    """Get venue information by name."""
    if not venue_name:
        return None
    
    venue_key = venue_name.lower().strip()
    
    # Direct match
    if venue_key in VENUES:
        return VENUES[venue_key]
    
    # Fuzzy match
    for key, info in VENUES.items():
        if key in venue_key or venue_key in key:
            return info
        if info["name"].lower() in venue_key or venue_key in info["name"].lower():
            return info
    
    return None


def add_venue(name: str, info: dict) -> None:
    """Add venue to database."""
    VENUES[name.lower().strip()] = info
