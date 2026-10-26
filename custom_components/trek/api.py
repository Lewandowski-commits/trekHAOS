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

    @property
    def _headers(self) -> Dict[str, str]:
        """Return default headers."""
        return {"Authorization": f"Bearer {self._api_key}"}

    async def get_trips(self) -> List[Dict[str, Any]]:
        """Get all trips."""
        try:
            async with self._session.get(f"{self._url}/api/v1/trips", headers=self._headers) as response:
                if response.status in (401, 403):
                    raise TrekApiAuthError("Not authenticated or invalid API key")
                response.raise_for_status()
                data = await response.json()
                
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "data" in data:
                    return data["data"]
                elif isinstance(data, dict) and "trips" in data:
                    return data["trips"]
                return data
        except aiohttp.ClientError as err:
            raise TrekApiClientError(f"Error communicating with API: {err}") from err

    async def get_stats(self) -> Dict[str, Any]:
        """Get travel stats."""
        try:
            async with self._session.get(f"{self._url}/api/v1/stats", headers=self._headers) as response:
                if response.status in (401, 403):
                    raise TrekApiAuthError("Not authenticated or invalid API key")
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            raise TrekApiClientError(f"Error communicating with API: {err}") from err

    async def get_bucket_list(self) -> List[Dict[str, Any]]:
        """Get bucket list."""
        try:
            async with self._session.get(f"{self._url}/api/v1/bucket-list", headers=self._headers) as response:
                if response.status in (401, 403):
                    raise TrekApiAuthError("Not authenticated or invalid API key")
                response.raise_for_status()
                data = await response.json()
                
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                return data
        except aiohttp.ClientError as err:
            raise TrekApiClientError(f"Error communicating with API: {err}") from err
