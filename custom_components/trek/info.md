# TREK Home Assistant Integration

This custom integration connects Home Assistant to your TREK trip planner instance. 

## Features
- **Calendar Integration**: See your trips directly in your Home Assistant Calendar.
- **Sensors**: 
  - `sensor.trek_active_trips`: Track how many trips are currently ongoing or upcoming.
  - `sensor.trek_next_trip`: Shows your next trip's destination and dates.

## Setup
After installing this integration via HACS, you must configure it:
1. Restart Home Assistant.
2. Go to **Settings > Devices & Services > Add Integration**.
3. Search for **TREK**.
4. Enter your TREK URL (e.g., `http://localhost:3000` if using the local Add-on, or your external TREK domain).
5. Provide your TREK Email and Password.

Your sensors and calendar will automatically populate!