"""Constants for the Regional Events integration."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "regional_events"

CONF_CITIES = "cities"
CITY_LIBEREC = "Liberec"
CITY_JABLONEC = "Jablonec"

URL_LIBEREC_PAGE = "https://www.visitliberec.eu/cz/akce-v-liberci/"
URL_JABLONEC_PAGE = "https://www.jablonec.com/calendar/"
URL_DFXS = "https://www.saldovo-divadlo.cz/program"
URL_LINSERKA = "https://linserka.cz/program/"
URL_LIPO_INK = "https://lipo.ink/cs/akce"
URL_ZIVY_LIBEREC = "https://zivyliberec.cz/akce"

DEFAULT_SCAN_INTERVAL = 360  # 6 hours in minutes
