import bluetooth

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1  # Use the same port that the sender is using
server_socket.bind(("", port))
server_socket.listen(1)

print("Waiting for a connection...")

client_socket, client_address = server_socket.accept()
print(f"Connected to {client_address}")

try:
    while True:
        data = client_socket.recv(1024)  # Receive up to 1024 bytes
        if not data:
            break
        print(f"Received: {data.decode('utf-8')}")
except KeyboardInterrupt:
    print("\nClosing connection.")
finally:
    client_socket.close()
    server_socket.close()
