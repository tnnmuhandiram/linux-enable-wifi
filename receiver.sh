#!/bin/bash

# Find Bluetooth Serial Port
BT_DEVICE=$(ls /dev/rfcomm*)

# Ensure a Bluetooth device is found
if [ -z "$BT_DEVICE" ]; then
    echo "No Bluetooth serial port found."
    exit 1
fi

echo "Listening on: $BT_DEVICE"

# Continuously read incoming messages
while true; do
    if read -r MESSAGE < "$BT_DEVICE"; then
        echo "Received message: $MESSAGE"

        # Send response back
        echo -e "Message received: $MESSAGE" > "$BT_DEVICE"
    fi
done
