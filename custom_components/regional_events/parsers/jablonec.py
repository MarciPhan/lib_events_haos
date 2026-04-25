"""Parser for Jablonec events."""
from datetime import datetime, date
import re
from bs4 import BeautifulSoup
import aiohttp
from ..const import LOGGER, CITY_JABLONEC
from ..models import RegionalEvent

URL_JABLONEC_PAGE = "https://www.365jablonec.cz/"

async def fetch_jablonec_events(session: aiohttp.ClientSession) -> list[RegionalEvent]:
    """Fetch events from 365jablonec.cz."""
    try:
        async with session.get(
            URL_JABLONEC_PAGE,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ) as response:
            if response.status != 200:
                LOGGER.error("Error fetching Jablonec events: %s", response.status)
                return []
            html = await response.text()
            return parse_jablonec_html(html)
    except Exception as err:
        LOGGER.exception("Unexpected error fetching Jablonec events: %s", err)
        return []

def parse_jablonec_html(html: str) -> list[RegionalEvent]:
    """Parse HTML from 365jablonec.cz."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Find all event containers
    for link in soup.find_all("a", href=re.compile(r"/udalosti-v-jablonci/(\d+)/")):
        container = link.find_parent(["div", "article", "li", "section"])
        if not container:
            continue
            
        text = container.get_text(strip=True, separator="|")
        
        try:
            # Parse date pattern like "25. 4."
            date_match = re.search(r"(\d+)\.\s*(\d+)\.", text)
            if not date_match:
                continue
                
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            
            if day > 31 or month > 12:
                continue
            
            # Handle year wrapping
            event_year = current_year
            if month < current_month:
                event_year += 1
            
            start_date = date(event_year, month, day)
            
            # Extract title
            title = link.get_text(strip=True) or "Akce"
            
            # Extract time
            time_match = re.search(r"(\d+:\d+)(?:\s*–\s*(\d+:\d+))?", text)
            time_str = time_match.group(0) if time_match else ""
            
            # Extract location (after time or from container)
            location = ""
            if time_match:
                location_part = text.split(time_match.group(0))[-1].strip("|").split("|")[0]
                location = location_part.strip()

            event_id = re.search(r"/udalosti-v-jablonci/(\d+)/", link["href"])
            uid = f"jbc_{event_id.group(1)}" if event_id else RegionalEvent.generate_uid(title, start_date, location)
            
            url = link.get("href", "")
            if url.startswith("/"):
                url = f"https://www.365jablonec.cz{url}"
            elif not url.startswith("http"):
                url = f"https://www.365jablonec.cz/{url}"
            
            description = f"Čas: {time_str}" if time_str else "Čas není znám"
            
            event = RegionalEvent(
                uid=uid,
                title=title,
                start=start_date,
                end=start_date,
                location=location or None,
                city=CITY_JABLONEC,
                category=None,
                description=description,
                url=url,
                image_url=None,
                source="365jablonec.cz"
            )
            events.append(event)
            
        except Exception as err:
            LOGGER.debug("Error parsing Jablonec event: %s", err)
            continue
    
    # Deduplicate by UID
    unique_events = {event.uid: event for event in events}
    return list(unique_events.values())
            
    # Deduplicate by UID
    unique_events = {}
    for e in events:
        if e["uid"] not in unique_events:
            unique_events[e["uid"]] = e
            
    return list(unique_events.values())
