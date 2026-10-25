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

    def __init__(self, url: str, email: str, password: str, session: aiohttp.ClientSession):
        """Initialize."""
        self._url = url.rstrip("/")
        self._email = email
        self._password = password
        self._session = session
        self._authenticated = False

    async def login(self) -> None:
        """Login to TREK."""
        try:
            async with self._session.post(
                f"{self._url}/api/auth/login",
                json={"email": self._email, "password": self._password}
            ) as response:
                if response.status in (401, 403):
                    raise TrekApiAuthError("Invalid credentials")
                response.raise_for_status()
                
                # The auth token might be in a cookie or returned as json
                # aiohttp ClientSession automatically handles cookies
                self._authenticated = True
        except aiohttp.ClientError as err:
            raise TrekApiClientError(f"Error communicating with API: {err}") from err

    async def get_trips(self) -> List[Dict[str, Any]]:
        """Get all trips."""
        if not self._authenticated:
            await self.login()
            
        try:
            async with self._session.get(f"{self._url}/api/trips") as response:
                if response.status in (401, 403):
                    self._authenticated = False
                    raise TrekApiAuthError("Not authenticated")
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
