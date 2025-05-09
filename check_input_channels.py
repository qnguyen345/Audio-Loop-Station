import sounddevice as sd

# Lists the available audio input devices in the system
# and displays their name and latency (s)
devices = sd.query_devices()
print("Available Audio Input Devices:")
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"Device {i}: {device['name']} (Low Latency: {device['default_low_input_latency']} sec)")
