import pyaudio

p = pyaudio.PyAudio()

p = pyaudio.PyAudio()
default_device_index = p.get_default_input_device_info()["index"]
print(f"Default Input Device Index: {default_device_index}")

info = p.get_device_info_by_index(default_device_index)
print(f"Device Name: {info['name']}")
print(f"Max Input Channels: {info['maxInputChannels']}")
print(f"Default Latency (Low): {info['defaultLowInputLatency']} sec")
print(f"Default Latency (High): {info['defaultHighInputLatency']} sec")

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}, Max Input Channels: {info['maxInputChannels']}, Default Low Latency: {info['defaultLowInputLatency']:.4f}s")

p.terminate()
