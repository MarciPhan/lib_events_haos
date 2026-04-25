"""Parser for Lipo.ink events."""
from datetime import datetime, date
from bs4 import BeautifulSoup
import aiohttp
from ..const import LOGGER, URL_LIPO_INK, CITY_LIBEREC
from ..models import RegionalEvent

async def fetch_lipo_events(session: aiohttp.ClientSession) -> list[RegionalEvent]:
    """Fetch events from lipo.ink."""
    try:
        async with session.get(
            URL_LIPO_INK,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as response:
            if response.status != 200:
                return []
            html = await response.text()
            return parse_lipo_html(html)
    except Exception as err:
        LOGGER.debug("Error fetching Lipo.ink events: %s", err)
        return []

def parse_lipo_html(html: str) -> list[RegionalEvent]:
    """Parse HTML from lipo.ink."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    
    for item in soup.select(".event-card"):
        try:
            title_el = item.select_one(".event-card__title")
            if not title_el:
                continue
                
            title = title_el.get_text(strip=True)
            date_str = item.select_one(".event-card__date").get_text(strip=True)
            
            # Format usually "2. 5. 2026"
            start_date = datetime.strptime(date_str, "%d. %m. %Y").date()
            location = "Lipo.ink"
            
            uid = RegionalEvent.generate_uid(title, start_date, location)
            
            event = RegionalEvent(
                uid=uid,
                title=title,
                start=start_date,
                end=start_date,
                location=location,
                city=CITY_LIBEREC,
                category="business",
                description="Workshop / Seminář v Lipo.ink",
                url=URL_LIPO_INK,
                source="Lipo.ink"
            )
            events.append(event)
        except Exception:
            continue
            
    return events
