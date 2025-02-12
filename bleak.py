from bleak import BleakServer

# Define UUIDs (must match the React Native app)
SERVICE_UUID = "12345678-1234-1234-1234-123456789012"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-210987654321"

async def main():
    server = BleakServer()

    # Add a custom service with a writable characteristic
    await server.add_service(
        SERVICE_UUID,
        {
            CHARACTERISTIC_UUID: {
                "write": lambda characteristic, value: print(f"Received: {value.decode('utf-8')}"),
                "read": False,
                "notify": False,
            }
        },
    )

    # Start the server
    await server.start()
    print("BLE server started. Waiting for connections...")

    # Keep the server running
    while True:
        await asyncio.sleep(1)

# Run the server
import asyncio
asyncio.run(main())
