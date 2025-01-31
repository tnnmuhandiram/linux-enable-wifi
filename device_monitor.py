import requests
import os
import time
import logging
import sys

# Configure logging
LOG_FILE = "/var/log/device_monitor.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

WEBHOOK_URL = "https://webhook.site/f51f3307-5125-4128-bb02-7497d2b6669c"

class DeviceMonitor:
    """ Ensures only one instance of the monitoring service runs. """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceMonitor, cls).__new__(cls)
        return cls._instance

    def send_webhook(self):
        """ Sends device status confirmation to the webhook. """
        try:
            payload = {
                "device_id": os.uname().nodename,
                "status": "running",
                "ip_address": self.get_ip_address(),
                "uptime": self.get_uptime()
            }
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
            logging.info("Webhook sent successfully: %s", response.text)
        except requests.RequestException as error:
            logging.error("Failed to send webhook: %s", error)

    @staticmethod
    def get_ip_address():
        """ Retrieves the device's IP address. """
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except socket.error:
            return "Unknown"

    @staticmethod
    def get_uptime():
        """ Retrieves the system uptime in seconds. """
        try:
            with open("/proc/uptime", "r", encoding="utf-8") as file:
                return float(file.readline().split()[0])
        except Exception as error:
            logging.error("Failed to read uptime: %s", error)
            return 0

def run_monitor():
    """ Main function to run the device monitor. """
    monitor = DeviceMonitor()
    monitor.send_webhook()

    # Keep running and checking periodically
    while True:
        time.sleep(3600)  # Sends update every hour

if __name__ == "__main__":
    pid = os.fork()
    if pid > 0:
        sys.exit()  # Exit parent process

    os.setsid()  # Create a new session
    pid = os.fork()
    if pid > 0:
        sys.exit()  # Exit first child process

    # Redirect standard file descriptors
    sys.stdout = open("/dev/null", "w")
    sys.stderr = open("/dev/null", "w")

    # Run the main monitoring function
    run_monitor()
