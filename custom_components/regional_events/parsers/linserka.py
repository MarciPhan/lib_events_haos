"""Parser for Linserka events."""
from datetime import datetime, date
from bs4 import BeautifulSoup
import aiohttp
from ..const import LOGGER, URL_LINSERKA, CITY_LIBEREC
from ..models import RegionalEvent

async def fetch_linserka_events(session: aiohttp.ClientSession) -> list[RegionalEvent]:
    """Fetch events from linserka.cz."""
    try:
        async with session.get(
            URL_LINSERKA,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as response:
            if response.status != 200:
                return []
            html = await response.text()
            return parse_linserka_html(html)
    except Exception as err:
        LOGGER.debug("Error fetching Linserka events: %s", err)
        return []

def parse_linserka_html(html: str) -> list[RegionalEvent]:
    """Parse HTML from linserka.cz."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    
    # Generic pattern for WordPress event sites (which Linserka often uses)
    for item in soup.select("article"):
        try:
            title_el = item.select_one("h2")
            if not title_el:
                continue
                
            title = title_el.get_text(strip=True)
            
            # Try to find date in text
            text = item.get_text()
            # Very simple date finding
            import re
            date_match = re.search(r"(\d+)\.\s*(\d+)\.", text)
            if not date_match:
                continue
            
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = datetime.now().year
            if month < datetime.now().month:
                year += 1
            
            start_date = date(year, month, day)
            location = "Linserka"
            
            uid = RegionalEvent.generate_uid(title, start_date, location)
            
            event = RegionalEvent(
                uid=uid,
                title=title,
                start=start_date,
                end=start_date,
                location=location,
                city=CITY_LIBEREC,
                category="kultura",
                description="Komunitní akce v Linserce",
                url=URL_LINSERKA,
                source="Linserka"
            )
            events.append(event)
        except Exception:
            continue
            
    return events
