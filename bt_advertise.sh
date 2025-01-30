#!/bin/bash

# Enable Bluetooth and configure settings
echo -e "power on\ndiscoverable on\npairable on\nadvertise on\nsystem-alias BitzifyGateway" | bluetoothctl

# Wait for a moment to ensure settings take effect
sleep 1

# Start advertising a service UUID (replace UUID with your actual service UUID)
SERVICE_UUID="0000180d-0000-1000-8000-00805f9b34fb"

echo -e "advertise uuids $SERVICE_UUID" | bluetoothctl
