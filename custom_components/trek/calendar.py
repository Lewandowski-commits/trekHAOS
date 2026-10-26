"""Calendar platform for TREK."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
    """Set up TREK calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([TrekCalendar(coordinator, entry)])


class TrekCalendar(CoordinatorEntity[TrekDataUpdateCoordinator], CalendarEntity):
    """TREK Calendar Entity."""

    def __init__(self, coordinator: TrekDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_name = "TREK Trips"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        if not self.coordinator.data or not self.coordinator.data.get("trips"):
            return None

        today = datetime.now().date()
        upcoming_events = []

        for trip in self.coordinator.data.get("trips", []):
            if trip.get("is_archived"):
                continue
                
            start_date_str = trip.get("start_date")
            end_date_str = trip.get("end_date")
            
            if not start_date_str:
                continue
                
            try:
                start_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d").date()
                if end_date_str:
                    end_date = datetime.strptime(end_date_str[:10], "%Y-%m-%d").date()
                    # Calendar events typically need end_date to be the day AFTER the last day of the event
                    # for an all-day event representation
                    end_date += timedelta(days=1)
                else:
                    end_date = start_date + timedelta(days=1)
                    
                if end_date > today:
                    event = CalendarEvent(
                        summary=trip.get("title", "Unnamed Trip"),
                        start=start_date,
                        end=end_date,
                        description=trip.get("description", ""),
                        location=trip.get("title", ""),
                    )
                    upcoming_events.append(event)
            except ValueError:
                continue

        if not upcoming_events:
            return None

        # Sort and return the first one
        upcoming_events.sort(key=lambda x: x.start)
        return upcoming_events[0]

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = []
        
        if not self.coordinator.data or not self.coordinator.data.get("trips"):
            return events

        start_date_d = start_date.date()
        end_date_d = end_date.date()

        for trip in self.coordinator.data.get("trips", []):
            if trip.get("is_archived"):
                continue

            trip_start_str = trip.get("start_date")
            trip_end_str = trip.get("end_date")

            if not trip_start_str:
                continue

            try:
                trip_start = datetime.strptime(trip_start_str[:10], "%Y-%m-%d").date()
                if trip_end_str:
                    trip_end = datetime.strptime(trip_end_str[:10], "%Y-%m-%d").date()
                    trip_end += timedelta(days=1)
                else:
                    trip_end = trip_start + timedelta(days=1)

                # Check if event overlaps with requested range
                if trip_start < end_date_d and trip_end > start_date_d:
                    events.append(
                        CalendarEvent(
                            summary=trip.get("title", "Unnamed Trip"),
                            start=trip_start,
                            end=trip_end,
                            description=trip.get("description", ""),
                            location=trip.get("title", ""),
                        )
                    )
            except ValueError:
                continue

        return events
