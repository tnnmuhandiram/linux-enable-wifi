import bluetooth
import os

def configure_wifi(ssid, password):
    # Update the wpa_supplicant.conf file
    wpa_supplicant_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
    config = f"""
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US

    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """
    with open(wpa_supplicant_path, "w") as file:
        file.write(config)
    
    # Restart the Wi-Fi service
    os.system("sudo systemctl restart dhcpcd")
    print("Wi-Fi configured and service restarted.")

def start_bluetooth_server():
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)
    
    port = server_socket.getsockname()[1]
    print(f"Listening for Bluetooth connections on port {port}...")

    bluetooth.advertise_service(server_socket, "WiFiSetup",
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    while True:
        print("Waiting for a connection...")
        client_socket, address = server_socket.accept()
        print(f"Accepted connection from {address}")

        try:
            data = client_socket.recv(1024).decode("utf-8").strip()
            print(f"Received data: {data}")
            if data:
                ssid, password = data.split(";")
                configure_wifi(ssid, password)
                client_socket.send("Wi-Fi configured successfully.".encode("utf-8"))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_bluetooth_server()
