"""Parser for Divadlo F. X. Šaldy events."""
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp
from ..const import LOGGER, URL_DFXS, CITY_LIBEREC
from ..models import RegionalEvent

async def fetch_dfxs_events(session: aiohttp.ClientSession) -> list[RegionalEvent]:
    """Fetch events from saldovo-divadlo.cz."""
    try:
        async with session.get(
            URL_DFXS,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as response:
            if response.status != 200:
                return []
            html = await response.text()
            return parse_dfxs_html(html)
    except Exception as err:
        LOGGER.debug("Error fetching DFXŠ events: %s", err)
        return []

def parse_dfxs_html(html: str) -> list[RegionalEvent]:
    """Parse HTML from saldovo-divadlo.cz."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    
    # Each play is usually in a div with a specific class
    for item in soup.select(".program-item"):
        try:
            title_el = item.select_one(".program-item__title")
            if not title_el:
                continue
                
            title = title_el.get_text(strip=True)
            date_str = item.select_one(".program-item__date").get_text(strip=True)
            time_str = item.select_one(".program-item__time").get_text(strip=True)
            
            # Format: "25. 4. 2026"
            start_date = datetime.strptime(date_str, "%d. %m. %Y").date()
            
            # DFXŠ has multiple stages
            location = "Šaldovo divadlo"
            stage_el = item.select_one(".program-item__stage")
            if stage_el:
                location = stage_el.get_text(strip=True)
            
            uid = RegionalEvent.generate_uid(title, start_date, location)
            
            event = RegionalEvent(
                uid=uid,
                title=title,
                start=start_date,
                end=start_date,
                location=location,
                city=CITY_LIBEREC,
                category="divadlo",
                description=f"Čas: {time_str}",
                url=URL_DFXS,
                source="DFXŠ"
            )
            events.append(event)
        except Exception:
            continue
            
    return events
