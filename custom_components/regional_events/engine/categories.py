"""Category normalization."""

CATEGORY_MAP = {
    "koncert": "music",
    "hudba": "music",
    "festival": "music",
    "divadlo": "theatre",
    "kino": "cinema",
    "film": "cinema",
    "výstava": "exhibition",
    "galerie": "exhibition",
    "workshop": "education",
    "kurz": "education",
    "školení": "education",
    "přednáška": "education",
    "seminář": "education",
    "děti": "kids",
    "pro děti": "kids",
    "program pro rodiny": "kids",
    "sport": "sports",
    "běh": "sports",
    "fotbal": "sports",
    "podnikání": "business",
    "startup": "business",
    "network": "business",
    "trh": "market",
    "jarmark": "market",
    "trhy": "market",
    "gastronomie": "food",
    "chutě": "food",
    "degustace": "food",
}

CS_CATEGORY_MAP = {
    "hudba": "music",
    "divadlo": "theatre",
    "kino": "cinema",
    "výstava": "exhibition",
    "vzdělání": "education",
    "děti": "kids",
    "sport": "sports",
    "podnikání": "business",
    "trhy": "market",
    "gastronomie": "food",
}


def normalize_category(category: str) -> str:
    """Normalize category name."""
    if not category:
        return "other"
    
    cat_lower = category.lower().strip()
    
    # Try exact match in both maps
    if cat_lower in CATEGORY_MAP:
        return CATEGORY_MAP[cat_lower]
    if cat_lower in CS_CATEGORY_MAP:
        return CS_CATEGORY_MAP[cat_lower]
    
    # Try substring match
    for key, value in CATEGORY_MAP.items():
        if key in cat_lower:
            return value
    
    for key, value in CS_CATEGORY_MAP.items():
        if key in cat_lower:
            return value
    
    return "other"


def get_category_display_name(category: str) -> str:
    """Get display name for category."""
    display_map = {
        "music": "🎵 Hudba",
        "theatre": "🎭 Divadlo",
        "cinema": "🎬 Kino",
        "exhibition": "🖼️ Výstava",
        "education": "📚 Vzdělání",
        "kids": "👶 Děti",
        "sports": "⚽ Sport",
        "business": "💼 Podnikání",
        "market": "🛍️ Trhy",
        "food": "🍽️ Gastronomie",
        "other": "📌 Ostatní",
    }
    return display_map.get(category, category)
