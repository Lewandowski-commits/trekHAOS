"""Data update coordinator for the TREK integration."""
import logging
from datetime import timedelta
from typing import Any, Dict, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TrekApi, TrekApiClientError, TrekApiAuthError
from .const import CONF_API_KEY, CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=15)

class TrekDataUpdateCoordinator(DataUpdateCoordinator[List[Dict[str, Any]]]):
    """Class to manage fetching TREK data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = TrekApi(
            url=entry.data[CONF_URL],
            api_key=entry.data[CONF_API_KEY],
            session=async_get_clientsession(hass),
        )
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> List[Dict[str, Any]]:
        """Update data via API."""
        try:
            trips = await self.api.get_trips()
            return trips
        except TrekApiAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except TrekApiClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
