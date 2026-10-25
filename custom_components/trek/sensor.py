"""Sensor platform for TREK."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TrekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TREK sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        TrekActiveTripsSensor(coordinator, entry),
        TrekNextTripSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class TrekActiveTripsSensor(CoordinatorEntity[TrekDataUpdateCoordinator], SensorEntity):
    """Sensor showing the number of active/upcoming trips."""

    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_active_trips"
        self._attr_name = "TREK Active Trips"
        self._attr_icon = "mdi:airplane-takeoff"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0
            
        count = 0
        today = datetime.now().date()
        
        for trip in self.coordinator.data:
            end_date_str = trip.get("end_date")
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str[:10], "%Y-%m-%d").date()
                    if end_date >= today:
                        count += 1
                except ValueError:
                    pass
            else:
                # If no end date, we might count it as active/upcoming depending on logic
                # Let's count it if it's not archived.
                if not trip.get("is_archived"):
                    count += 1
                    
        return count


class TrekNextTripSensor(CoordinatorEntity[TrekDataUpdateCoordinator], SensorEntity):
    """Sensor showing the next upcoming trip."""

    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_trip"
        self._attr_name = "TREK Next Trip"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "No trips"
            
        upcoming_trips = []
        today = datetime.now().date()
        
        for trip in self.coordinator.data:
            start_date_str = trip.get("start_date")
            if start_date_str and not trip.get("is_archived"):
                try:
                    start_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d").date()
                    if start_date >= today:
                        upcoming_trips.append((start_date, trip.get("title", "Unnamed Trip")))
                except ValueError:
                    pass
                    
        if not upcoming_trips:
            return "No upcoming trips"
            
        upcoming_trips.sort(key=lambda x: x[0])
        return upcoming_trips[0][1]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        upcoming_trips = []
        today = datetime.now().date()
        
        for trip in self.coordinator.data:
            start_date_str = trip.get("start_date")
            if start_date_str and not trip.get("is_archived"):
                try:
                    start_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d").date()
                    if start_date >= today:
                        upcoming_trips.append((start_date, trip))
                except ValueError:
                    pass
                    
        if not upcoming_trips:
            return {}
            
        upcoming_trips.sort(key=lambda x: x[0])
        next_trip = upcoming_trips[0][1]
        
        return {
            "start_date": next_trip.get("start_date"),
            "end_date": next_trip.get("end_date"),
            "destination": next_trip.get("title"),
            "id": next_trip.get("id"),
        }
