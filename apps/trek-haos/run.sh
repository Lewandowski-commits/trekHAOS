#!/bin/sh

# Start the sync script in the background
echo "Starting HA users sync script..."
python3 /sync.py &

# Start the main application using the original command
echo "Starting TREK application..."
exec /usr/local/bin/trek-entrypoint
