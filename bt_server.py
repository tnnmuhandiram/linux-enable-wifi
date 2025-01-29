import bluetooth

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = bluetooth.PORT_ANY  # Use any available port
server_socket.bind(("", port))
server_socket.listen(1)

print(f"Waiting for connection on RFCOMM channel {port}...")
bluetooth.advertise_service(
    server_socket,
    "BluetoothServer",
    service_id="00001101-0000-1000-8000-00805f9b34fb",  # Serial Port Profile (SPP) UUID
    service_classes=["00001101-0000-1000-8000-00805f9b34fb", bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

client_socket, client_info = server_socket.accept()
print(f"Accepted connection from {client_info}")

try:
    while True:
        data = client_socket.recv(1024).decode("utf-8")
        if data:
            print(f"Received: {data}")
            client_socket.send(f"Echo: {data}".encode("utf-8"))
except OSError:
    print("Connection closed.")
finally:
    client_socket.close()
    server_socket.close()
