"""Parser for Liberec events."""
from datetime import datetime, date
import re
from bs4 import BeautifulSoup
import aiohttp
from ..const import LOGGER, URL_LIBEREC_PAGE, CITY_LIBEREC
from ..models import RegionalEvent

async def fetch_liberec_events(session: aiohttp.ClientSession) -> list[RegionalEvent]:
    """Fetch events from visitliberec.eu."""
    try:
        async with session.get(
            URL_LIBEREC_PAGE,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ) as response:
            if response.status != 200:
                LOGGER.error("Error fetching Liberec events: %s", response.status)
                return []
            html = await response.text()
            return parse_liberec_html(html)
    except Exception as err:
        LOGGER.exception("Unexpected error fetching Liberec events: %s", err)
        return []

def parse_liberec_html(html: str):
    """Parse HTML from visitliberec.eu."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    
    # Each event is in an <a> tag with class "event-item" or similar
    # Looking at the markdown, they seem to be in containers
    # Let's find the correct selector. In the markdown they look like links with nested info.
    
    # Based on the markdown structure:
    # [Humanitární akceSbírka potravin - jaro 2026So 25. 4.8:00–18:00Liberec](URL)
    
    # Let's assume a common structure for these sites (often they use a div with class "item" or "event")
    # Actually, I'll use a more generic approach finding links containing date patterns.
    
def parse_liberec_html(html: str) -> list[RegionalEvent]:
    """Parse HTML from visitliberec.eu."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Find all event links
    for link in soup.find_all("a", href=re.compile(r"e=\d+")):
        text = link.get_text(strip=True, separator="|")
        parts = [p.strip() for p in text.split("|") if p.strip()]
        
        if len(parts) < 2:
            continue
            
        try:
            # Try to find date pattern
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
            
            # Extract category (usually first part or empty)
            category = parts[0] if len(parts) > 2 else None
            
            # Extract title (usually second part or first if no category)
            title = parts[1] if category else parts[0]
            
            # Try to find time
            time_match = re.search(r"(\d+:\d+)(?:–(\d+:\d+))?", text)
            time_str = time_match.group(0) if time_match else ""
            
            # Location is usually the last part
            location = parts[-1] if len(parts) > 2 else None
            
            # Extract event ID from URL
            event_id = re.search(r"e=(\d+)", link.get("href", ""))
            uid = f"lbc_{event_id.group(1)}" if event_id else RegionalEvent.generate_uid(title, start_date, location)
            
            url = link.get("href", "")
            if not url.startswith("http"):
                if url.startswith("/"):
                    url = f"https://www.visitliberec.eu{url}"
                else:
                    url = f"https://www.visitliberec.eu/{url}"
            
            description = f"Čas: {time_str}" if time_str else ""
            if category:
                description = f"Kategorie: {category}\n{description}".strip()
            
            event = RegionalEvent(
                uid=uid,
                title=title,
                start=start_date,
                end=start_date,
                location=location,
                city=CITY_LIBEREC,
                category=category,
                description=description or None,
                url=url,
                image_url=None,
                source="visitliberec.eu"
            )
            events.append(event)
            
        except Exception as err:
            LOGGER.debug("Error parsing Liberec event: %s", err)
            continue
    
    # Deduplicate by UID
    unique_events = {event.uid: event for event in events}
    return list(unique_events.values())
