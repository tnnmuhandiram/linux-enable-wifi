from pydbus import SystemBus
from gi.repository import GLib

bus = SystemBus()
print("D-Bus system bus connected successfully!")

loop = GLib.MainLoop()
loop.quit()  # Exiting the loop immediately for testing
print("GLib is working correctly!")
