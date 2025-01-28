from bleak import BleakServer
from bleak.backends.characteristic import BleakGATTCharacteristic
import os
import subprocess
import time
import requests

UUID_FILE = '/etc/device_uuid'
WPA_SUPPLICANT_CONF = '/etc/wpa_supplicant/wpa_supplicant.conf'
WEBHOOK_URL = 'https://webhook.site/620cfed8-020c-4676-aa89-5fd2d6dc39e7'

# Define UUIDs for BLE services and characteristics
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"

# BLE characteristic write handler
async def characteristic_write_handler(characteristic, value):
    try:
        data = value.decode("utf-8").strip()
        print(f"Received data: {data}")
        if data:
            ssid, password, uuid = data.split(";")
            configure_wifi(ssid, password)
            save_uuid(uuid)

            # Check internet connection and trigger webhook
            for _ in range(10):  # Retry up to 10 times
                if check_internet():
                    print("Internet connected.")
                    trigger_webhook(uuid)
                    return f"Wi-Fi configured and webhook triggered successfully."
                time.sleep(5)
            else:
                return "Wi-Fi configured but failed to connect to the internet."
    except Exception as e:
        print(f"Error: {e}")
        return "Error processing data."

# Wi-Fi configuration function
def configure_wifi(ssid, password):
    """Update the wpa_supplicant.conf file and restart Wi-Fi service."""
    config = f"""
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US
    network={{
        ssid=\"{ssid}\"
        psk=\"{password}\"
    }}
    """
    with open(WPA_SUPPLICANT_CONF, "w") as file:
        file.write(config)
    os.system("sudo systemctl restart dhcpcd")
    print("Wi-Fi configured and service restarted.")

# Save UUID function
def save_uuid(uuid):
    """Save the UUID locally."""
    with open(UUID_FILE, 'w') as f:
        f.write(uuid)

# Internet connection check function
def check_internet():
    """Check if the device is connected to the internet."""
    try:
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# Trigger webhook function
def trigger_webhook(uuid):
    """Trigger a device live webhook with the UUID."""
    data = {'uuid': uuid}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("Device is live.")
    except requests.RequestException as e:
        print(f"Failed to trigger webhook: {e}")

# BLE server setup
async def start_ble_server():
    """Start the BLE GATT server."""
    characteristic = BleakGATTCharacteristic(
        CHARACTERISTIC_UUID,
        ["write"],
        write_handler=characteristic_write_handler,
    )

    server = BleakServer()
    await server.add_service(SERVICE_UUID, [characteristic])
    
    print(f"BLE server started with service UUID: {SERVICE_UUID}")
    await server.start()

# Main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(start_ble_server())
