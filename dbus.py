from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property, signal
from dbus_next.constants import PropertyAccess
from dbus_next import Variant

import asyncio

SERVICE_UUID = "12345678-1234-1234-1234-123456789012"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-210987654321"

class ExampleService(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.ExampleService")

    @method()
    def WriteValue(self, value: "ay"):
        print(f"Received: {bytes(value).decode('utf-8')}")

async def main():
    bus = await MessageBus().connect()

    service = ExampleService()
    bus.export("/org/bluez/example/service", service)

    await bus.request_name("org.bluez.ExampleService")

    print("BLE server started. Waiting for connections...")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
