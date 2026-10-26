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
        TrekTotalTripsSensor(coordinator, entry),
        TrekTotalCountriesSensor(coordinator, entry),
        TrekTotalCitiesSensor(coordinator, entry),
        TrekTotalPlacesSensor(coordinator, entry),
        TrekTotalDaysSensor(coordinator, entry),
        TrekTotalDistanceSensor(coordinator, entry),
        TrekDaysUntilNextTripSensor(coordinator, entry),
        TrekLastTripSensor(coordinator, entry),
        TrekBucketListSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class TrekBaseSensor(CoordinatorEntity[TrekDataUpdateCoordinator], SensorEntity):
    """Base class for TREK sensors."""
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry, key: str, name: str, icon: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = f"TREK {name}"
        self._attr_icon = icon

    @property
    def stats(self) -> Dict[str, Any]:
        """Return stats dictionary from coordinator."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("stats", {})


class TrekActiveTripsSensor(TrekBaseSensor):
    """Sensor showing the number of active/upcoming trips."""
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "active_trips", "Active Trips", "mdi:airplane-takeoff")

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
            
        count = 0
        today = datetime.now().date()
        
        for trip in self.coordinator.data.get("trips", []):
            end_date_str = trip.get("end_date")
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str[:10], "%Y-%m-%d").date()
                    if end_date >= today:
                        count += 1
                except ValueError:
                    pass
            else:
                if not trip.get("is_archived"):
                    count += 1
                    
        return count


class TrekNextTripSensor(TrekBaseSensor):
    """Sensor showing the next upcoming trip."""
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "next_trip", "Next Trip", "mdi:calendar-clock")

    @property
    def native_value(self) -> str | None:
        next_trip = self.stats.get("next_trip")
        if not next_trip:
            return "No upcoming trips"
        return next_trip.get("title", "Unnamed Trip")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        next_trip = self.stats.get("next_trip")
        if not next_trip:
            return {}
        
        return {
            "start_date": next_trip.get("start_date"),
            "end_date": next_trip.get("end_date"),
            "days_until": next_trip.get("days_until"),
            "country": next_trip.get("country"),
            "countries": next_trip.get("countries", []),
class TrekTotalTripsSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "total_trips", "Total Trips", "mdi:bag-suitcase")

    @property
    def native_value(self) -> int | None:
        return self.stats.get("total_trips")


class TrekTotalCountriesSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "total_countries", "Total Countries", "mdi:earth")

    @property
    def native_value(self) -> int | None:
        return self.stats.get("total_countries")


class TrekTotalCitiesSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "total_cities", "Total Cities", "mdi:city")

    @property
    def native_value(self) -> int | None:
        return self.stats.get("total_cities")


class TrekTotalPlacesSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "total_places", "Total Places", "mdi:map-marker-multiple")

    @property
    def native_value(self) -> int | None:
        return self.stats.get("total_places")


class TrekTotalDaysSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "total_days", "Total Days Travelled", "mdi:calendar-range")

    @property
    def native_value(self) -> int | None:
        return self.stats.get("total_days")


class TrekTotalDistanceSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "total_distance", "Total Distance Flown", "mdi:airplane")
        self._attr_native_unit_of_measurement = "km"
        self._attr_device_class = "distance"

    @property
    def native_value(self) -> float | None:
        return self.stats.get("total_distance_km")


class TrekDaysUntilNextTripSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "days_until_next_trip", "Days Until Next Trip", "mdi:timer-sand")
        self._attr_native_unit_of_measurement = "days"

    @property
    def native_value(self) -> int | None:
        next_trip = self.stats.get("next_trip")
        if not next_trip:
            return None
        return next_trip.get("days_until")


class TrekLastTripSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_trip", "Last Trip", "mdi:history")

    @property
    def native_value(self) -> str | None:
        last_trip = self.stats.get("last_trip")
        if not last_trip:
            return "No previous trips"
        return last_trip.get("title", "Unnamed Trip")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        last_trip = self.stats.get("last_trip")
        if not last_trip:
            return {}
        
        return {
            "start_date": last_trip.get("start_date"),
            "end_date": last_trip.get("end_date"),
            "country": last_trip.get("country"),
            "countries": last_trip.get("countries", []),
        }


class TrekBucketListSensor(TrekBaseSensor):
    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "bucket_list", "Bucket List", "mdi:format-list-checks")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return 0
        bucket_list = self.coordinator.data.get("bucket_list", [])
        return len(bucket_list)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        if not self.coordinator.data:
            return {}
        bucket_list = self.coordinator.data.get("bucket_list", [])
        
        items = [item.get("name", "Unnamed") for item in bucket_list]
        return {
            "items": items
        }
