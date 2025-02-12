from pydbus import SystemBus
from gi.repository import GLib

SERVICE_UUID = "0000abcd-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000dcba-0000-1000-8000-00805f9b34fb"

class BLECharacteristic:
    def __init__(self, uuid, flags):
        self.uuid = uuid
        self.flags = flags  # Ensure "write" is included for data transfer
        self.value = bytearray("Init", "utf-8")

    def WriteValue(self, value, options):
        self.value = value
        print(f"Received Data: {value.decode()}")

class BLEService:
    def __init__(self, uuid):
        self.uuid = uuid
        self.characteristics = [BLECharacteristic(CHARACTERISTIC_UUID, ["write", "read"])]
        self.keep_alive = True  # ✅ Prevents disconnection

def start_ble_server():
    bus = SystemBus()
    service = BLEService(SERVICE_UUID)

    print("BLE Service Running with Persistent Connection...")
    GLib.MainLoop().run()

start_ble_server()
