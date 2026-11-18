import pywinusb.hid as hid
import time
import sys

def device_event(event_type, device):
    """Callback when HID device is added/removed"""
    if event_type == 'arrival':
        vid = hex(device.vendor_id)
        pid = hex(device.product_id)
        name = device.product_name or 'unknown'
        print(f"[+] HID ARRIVED: VID={vid} PID={pid} {name}")
    elif event_type == 'removal':
        vid = hex(device.vendor_id)
        pid = hex(device.product_id) 
        name = device.product_name or 'unknown'
        print(f"[-] HID REMOVED: VID={vid} PID={pid} {name}")

print("Monitoring HID devices for STC USB ISP...")
print("Press Ctrl+C to stop")
print()

# Register for device notifications
hid.HidDeviceMonitor(hid.HidDeviceFilter(), device_event)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped")
    sys.exit(0)
