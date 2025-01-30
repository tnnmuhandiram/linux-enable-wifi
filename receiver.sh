#!/bin/bash

# The UUID of the characteristic where we expect to receive data
CHAR_UUID="00002a39-0000-1000-8000-00805f9b34fb"

# Make sure Bluetooth is powered on
bluetoothctl power on

# Scan for incoming connections
echo "Waiting for Bluetooth connection..."
bluetoothctl scan on & sleep 5
bluetoothctl scan off

# Start listening
echo "Listening for BLE data..."

gatttool -t random -b XX:XX:XX:XX:XX:XX --char-read --uuid=$CHAR_UUID | while read data; do
    # Convert received HEX data back to text
    RECEIVED_TEXT=$(echo $data | cut -d":" -f2 | xxd -r -p)
    echo "Received: $RECEIVED_TEXT"
done
