import os
import time
import paho.mqtt.client as mqtt
import adafruit_dht
import board
import ssl

# Load environment variables from Docker container
IOT_HUB_HOSTNAME = "acgdemoiot.azure-devices.net"  # Example: myiothub.azure-devices.net
DEVICE_ID = "acgdemobitzify1"  # Example: sensor-device-001
SAS_TOKEN = "pG9NOhPKnxgG+2uVTOKDankdYwTzlvWgw/4XGmDk"  # sample Shared Access Signature for authentication
SEND_TELEMETRY = "start"

MQTT_TOPIC = f"devices/{DEVICE_ID}/messages/events/"
MQTT_BROKER = IOT_HUB_HOSTNAME

# Try initializing the DHT11 sensor on GPIO pin 4
try:
    dht_device = adafruit_dht.DHT11(board.D4)
    sensor_available = True
except Exception as e:
    print(f"⚠️ Warning: Could not initialize DHT11 sensor. Error: {e}")
    sensor_available = False

# Setup MQTT client
client = mqtt.Client(client_id=DEVICE_ID, protocol=mqtt.MQTTv311)
client.username_pw_set(username=f"{IOT_HUB_HOSTNAME}/{DEVICE_ID}/?api-version=2021-04-12", password=SAS_TOKEN)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect(MQTT_BROKER, 8883, 60)

def read_sensor():
    """Reads temperature and humidity from DHT11 sensor."""
    if not sensor_available:
        print("⚠️ Sensor not available. Skipping data collection.")
        return None

    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if humidity is not None and temperature is not None:
            return {"temperature": temperature, "humidity": humidity}
    except RuntimeError as error:
        print(f"⚠️ Sensor error: {error}")
    return None

def send_data():
    """Send telemetry data to Azure IoT Hub."""
    global SEND_TELEMETRY
    while SEND_TELEMETRY == "start":
        data = read_sensor()
        if data:
            message = f'{{"temperature": {data["temperature"]}, "humidity": {data["humidity"]}}}'
            print(f"📡 Sending: {message}")
            client.publish(MQTT_TOPIC, message)
        time.sleep(5)

if __name__ == "__main__":
    print("🚀 Starting MQTT Sensor Application...")
    client.loop_start()
    while True:
        SEND_TELEMETRY = os.getenv("SEND_TELEMETRY", "start")  # Continuously check if telemetry should be sent
        if SEND_TELEMETRY == "start":
            send_data()
        elif SEND_TELEMETRY == "stop":
            print("⏸️ Stopping telemetry...")
            time.sleep(5)
        else:
            print(f"⚠️ Invalid command: '{SEND_TELEMETRY}'. Waiting for correct input...")
            time.sleep(5)
