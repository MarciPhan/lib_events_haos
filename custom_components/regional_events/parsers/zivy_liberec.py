"""Parser for Živý Liberec events."""
from datetime import datetime, date
from bs4 import BeautifulSoup
import aiohttp
from ..const import LOGGER, URL_ZIVY_LIBEREC, CITY_LIBEREC
from ..models import RegionalEvent

async def fetch_zivy_liberec_events(session: aiohttp.ClientSession) -> list[RegionalEvent]:
    """Fetch events from zivyliberec.cz."""
    try:
        async with session.get(
            URL_ZIVY_LIBEREC,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as response:
            if response.status != 200:
                return []
            html = await response.text()
            return parse_zivy_html(html)
    except Exception as err:
        LOGGER.debug("Error fetching Živý Liberec events: %s", err)
        return []

def parse_zivy_html(html: str) -> list[RegionalEvent]:
    """Parse HTML from zivyliberec.cz."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    
    for item in soup.select(".akce-item"):
        try:
            title_el = item.select_one(".akce-item__title")
            if not title_el:
                continue
                
            title = title_el.get_text(strip=True)
            date_str = item.select_one(".akce-item__date").get_text(strip=True)
            
            # Format usually "2. 5. 2026"
            start_date = datetime.strptime(date_str, "%d. %m. %Y").date()
            location = item.select_one(".akce-item__place").get_text(strip=True) if item.select_one(".akce-item__place") else "Liberec"
            
            uid = RegionalEvent.generate_uid(title, start_date, location)
            
            event = RegionalEvent(
                uid=uid,
                title=title,
                start=start_date,
                end=start_date,
                location=location,
                city=CITY_LIBEREC,
                category="kultura",
                description="Kulturní akce v Liberci",
                url=URL_ZIVY_LIBEREC,
                source="Živý Liberec"
            )
            events.append(event)
        except Exception:
            continue
            
    return events
