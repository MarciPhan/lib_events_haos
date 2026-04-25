"""Services for Regional Events integration."""
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, LOGGER

SERVICE_REFRESH = "refresh_events"
SERVICE_GENERATE_DIGEST = "generate_digest"

DIGEST_SCHEMA = vol.Schema({
    vol.Optional("period", default="weekend"): vol.In(["today", "tomorrow", "weekend", "week"]),
    vol.Optional("max_events", default=5): vol.Coerce(int),
    vol.Optional("min_score", default=60): vol.Coerce(float),
    vol.Optional("use_ai", default=False): vol.Coerce(bool),
    vol.Optional("ai_agent", default="conversation.home"): cv.string,
})

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the integration."""
    
    async def handle_refresh(call: ServiceCall) -> None:
        """Handle refresh service call."""
        LOGGER.info("Refreshing regional events via service")
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            await coordinator.async_refresh()

    async def handle_generate_digest(call: ServiceCall) -> None:
        """Handle digest generation service call."""
        period = call.data.get("period")
        max_events = call.data.get("max_events")
        min_score = call.data.get("min_score")
        use_ai = call.data.get("use_ai")
        ai_agent = call.data.get("ai_agent")
        
        # Collect all events
        all_events = []
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]
            all_events.extend(coordinator.all_events)
            
        from datetime import datetime, timedelta
        now = datetime.now()
        
        filtered = []
        for event in all_events:
            if event.score < min_score: continue
            e_date = event.start.date() if hasattr(event.start, 'date') else event.start
            if period == "today" and e_date == now.date(): filtered.append(event)
            elif period == "tomorrow" and e_date == (now + timedelta(days=1)).date(): filtered.append(event)
            elif period == "weekend" and e_date.weekday() in [5, 6] and e_date >= now.date(): filtered.append(event)
            elif period == "week" and now.date() <= e_date <= (now + timedelta(days=7)).date(): filtered.append(event)
        
        filtered.sort(key=lambda x: x.score, reverse=True)
        top_events = filtered[:max_events]
        
        if not top_events:
            text = f"Žádné zajímavé akce pro období {period} nenalezeny."
        elif use_ai:
            # Construct prompt for AI
            prompt = f"Udělej mi stručný a lákavý víkendový plán na {period} z těchto akcí:\n"
            for e in top_events:
                prompt += f"- {e.title}: {e.start}, {e.location}, skóre {e.score}%, důvod: {', '.join(e.reasoning or [])}\n"
            prompt += "\nPiš česky, buď osobní a doporuč to nejlepší podle počasí a nálady."
            
            try:
                # Call HA conversation agent
                from homeassistant.components import conversation
                ai_result = await hass.services.async_call(
                    "conversation",
                    "process",
                    {"text": prompt, "agent_id": ai_agent},
                    blocking=True,
                    return_response=True
                )
                text = ai_result.get("response", {}).get("speech", {}).get("plain", {}).get("speech", "Chyba AI.")
            except Exception as e:
                LOGGER.error("AI Digest error: %s", e)
                text = "Nepodařilo se vygenerovat AI souhrn."
        else:
            text = f"Doporučené akce na {period}:\n\n"
            for i, event in enumerate(top_events, 1):
                text += f"{i}. {event.title} ({event.score}%)\n"
                text += f"   📍 {event.location or event.city}\n"
                if event.reasoning: text += f"   💡 {event.reasoning[0]}\n"
                text += "\n"
        
        hass.bus.async_fire(f"{DOMAIN}_digest_generated", {"text": text})
        hass.states.async_set(f"sensor.{DOMAIN}_digest", text, {"period": period})

    hass.services.async_register(DOMAIN, SERVICE_REFRESH, handle_refresh)
    hass.services.async_register(DOMAIN, SERVICE_GENERATE_DIGEST, handle_generate_digest, schema=DIGEST_SCHEMA)
