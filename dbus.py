from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property, signal
from dbus_next.constants import PropertyAccess
from dbus_next import Variant

import asyncio

# UUIDs for the custom service and characteristic
SERVICE_UUID = "12345678-1234-1234-1234-123456789012"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-210987654321"

class ExampleService(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.ExampleService")

    @method()
    def WriteValue(self, value: "ay"):
        print(f"Received: {bytes(value).decode('utf-8')}")

async def main():
    # Connect to the system bus
    bus = await MessageBus().connect()

    # Create the custom service
    service = ExampleService()
    bus.export("/org/bluez/example/service", service)

    # Request a name on the bus
    await bus.request_name("org.bluez.ExampleService")

    # Advertise the service
    adapter = await bus.get_proxy_object(
        "org.bluez",
        "/org/bluez/hci0",
        "org.bluez.Adapter1"
    )

    # Set the adapter to be discoverable
    await adapter.set_discoverable(True)
    print("Adapter is now discoverable...")

    # Advertise the custom service UUID
    await adapter.set_discoverable_timeout(0)  # 0 means no timeout
    await adapter.set_advertising_data({
        "ServiceUUIDs": Variant("as", [SERVICE_UUID])
    })
    print(f"Advertising service UUID: {SERVICE_UUID}")

    print("BLE server started. Waiting for connections...")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
