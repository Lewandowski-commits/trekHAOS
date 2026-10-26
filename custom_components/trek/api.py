"""API client for TREK."""
import logging
from typing import Any, Dict, List

import aiohttp

_LOGGER = logging.getLogger(__name__)

class TrekApiClientError(Exception):
    """Exception to indicate a general API error."""

class TrekApiAuthError(TrekApiClientError):
    """Exception to indicate an authentication error."""

class TrekApi:
    """TREK API Client."""

    def __init__(self, url: str, api_key: str, session: aiohttp.ClientSession):
        """Initialize."""
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._session = session

    async def get_trips(self) -> List[Dict[str, Any]]:
        """Get all trips."""
        headers = {
            "Authorization": f"Bearer {self._api_key}"
        }
            
        try:
            async with self._session.get(f"{self._url}/api/trips", headers=headers) as response:
                if response.status in (401, 403):
                    raise TrekApiAuthError("Not authenticated or invalid API key")
                response.raise_for_status()
                data = await response.json()
                
                # Depending on how the API returns trips, it might be in a 'data' field or a direct array
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "data" in data:
                    return data["data"]
                elif isinstance(data, dict) and "trips" in data:
                    return data["trips"]
                return data
        except aiohttp.ClientError as err:
            raise TrekApiClientError(f"Error communicating with API: {err}") from err
