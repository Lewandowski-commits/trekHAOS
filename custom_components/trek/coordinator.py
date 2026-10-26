"""Data update coordinator for the TREK integration."""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TrekApi, TrekApiClientError, TrekApiAuthError
from .const import CONF_API_KEY, CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=15)

class TrekDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
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

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API."""
        try:
            # We fetch all data concurrently to speed up the update process
            trips_task = self.api.get_trips()
            stats_task = self.api.get_stats()
            bucket_list_task = self.api.get_bucket_list()
            
            results = await asyncio.gather(trips_task, stats_task, bucket_list_task, return_exceptions=True)
            
            # Check if any task failed with an Auth Error
            for result in results:
                if isinstance(result, TrekApiAuthError):
                    raise TrekApiAuthError(f"Authentication error: {result}")
            
            trips = results[0] if not isinstance(results[0], Exception) else []
            stats = results[1] if not isinstance(results[1], Exception) else {}
            bucket_list = results[2] if not isinstance(results[2], Exception) else []
            
            return {
                "trips": trips,
                "stats": stats,
                "bucket_list": bucket_list,
            }
            
        except TrekApiAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except TrekApiClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
