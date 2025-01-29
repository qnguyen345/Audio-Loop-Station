import pyaudio
import numpy as np
import threading
import time

# Constants
CHUNK = 1024  # Frames per buffer
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
BPM = 120  # Set your desired tempo
BEATS_PER_LOOP = 4  # Number of beats per loop
FRAMES_PER_LOOP = int((60 / BPM) * BEATS_PER_LOOP * RATE) # Calculate loop length in frames
print(f"Loop duration: {FRAMES_PER_LOOP} samples ({BEATS_PER_LOOP} beats at {BPM} BPM)")

def generate_click(sample_rate=RATE, duration_ms=50, frequency=1000):
    """Generate a short click sound."""
    duration_samples = int((duration_ms / 1000) * sample_rate)
    t = np.linspace(0, duration_ms / 1000, duration_samples, False)
    click = (np.sin(2 * np.pi * frequency * t) * 0.5 * 32767).astype(np.int16)
    return click.reshape(-1, 1)  # Ensure mono output

class LoopMachine:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        
        # Allocate memory for multiple looping tracks (each is FRAMES_PER_LOOP long)
        self.loops = []  # List of recorded loop buffers
        self.current_recording = None  # Active buffer being recorded
        self.recording_index = 0  # Which loop segment we're recording into
        self.is_recording = False  # Flag to track recording state
        self.position = 0  # Tracks the playback/recording position

        # Open input stream for recording
        self.input_stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        # Open output stream for playback
        self.output_stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.audio_callback
        )

        self.output_stream.start_stream()

    def start_recording(self):
        """Start a new loop recording."""
        print("start_recording() called")  # Debugging
        self.is_recording = True
        self.current_recording = np.zeros((FRAMES_PER_LOOP, CHANNELS), dtype=np.int16)
        self.recording_index = len(self.loops)  # New segment
        print(f"Recording started. Loops recorded so far: {len(self.loops)}")

    def stop_recording(self):
        """Stop recording and discard the current incomplete segment."""
        self.is_recording = False
        self.current_recording = None
        print(f"Recorded Loops: {len(self.loops)}")

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Handles both playback and recording in sync."""

        # print(f"audio_callback called. is_recording={self.is_recording}, in_data={in_data is not None}")  # Debugging

        global_audio_out = np.zeros((frame_count, 1), dtype=np.int16)  # Mono output

        # Only process input data if we're recording
        if self.is_recording:
            try:
                in_data = self.input_stream.read(frame_count, exception_on_overflow=False)
                input_audio = np.frombuffer(in_data, dtype=np.int16).reshape(-1, 1)  # Mono
            except IOError as e:
                print(f"Input stream read error: {e}")
                input_audio = np.zeros((frame_count, 1), dtype=np.int16)  # Silence fallback

            # Write input to the current recording segment
            start_idx = self.position
            end_idx = self.position + frame_count

            print(f"Recording position: {start_idx} to {end_idx}")

            if end_idx >= FRAMES_PER_LOOP:
                # Wrap around if reaching the end
                first_part = input_audio[:FRAMES_PER_LOOP - start_idx]
                second_part = input_audio[FRAMES_PER_LOOP - start_idx:]

                self.current_recording[start_idx:] = first_part
                print(f"Saving loop of length: {len(self.current_recording)}")
                self.loops.append(self.current_recording)  # Store finished segment

                # Start a new segment
                self.current_recording = np.zeros((FRAMES_PER_LOOP, 1), dtype=np.int16)
                self.current_recording[:len(second_part)] = second_part
            else:
                # Fill the current recording buffer
                self.current_recording[start_idx:end_idx] = input_audio

        # Mix playback audio from existing recorded loops
        for loop in self.loops:
            end_idx = self.position + frame_count

            if end_idx > len(loop):
                # Wrap around: split the read into two parts
                first_part = loop[self.position:]  # Read until the end
                second_part = loop[:end_idx - len(loop)]  # Read from start of loop
                mixed_output = np.vstack((first_part, second_part))
            else:
                mixed_output = loop[self.position:end_idx]

            # Ensure the output shape matches frame_count before mixing
            if mixed_output.shape[0] < frame_count:
                padding = np.zeros((frame_count - mixed_output.shape[0], 1), dtype=np.int16)
                mixed_output = np.vstack((mixed_output, padding))  # Zero-pad to avoid shape mismatch

            global_audio_out += mixed_output

        # Prevent clipping
        global_audio_out = np.clip(global_audio_out, -32768, 32767)

        # Move playback position forward
        self.position += frame_count
        if self.position >= FRAMES_PER_LOOP:
            self.position = 0  # Loop back to start

        return (global_audio_out.tobytes(), pyaudio.paContinue)

    def stop(self):
        """Stops playback and cleans up resources."""
        self.is_recording = False
        self.output_stream.stop_stream()
        self.output_stream.close()
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.p.terminate()

# Run the loop machine
if __name__ == "__main__":
    loop_machine = LoopMachine()

    try:
        while True:
            cmd = input("Enter 'r' to start recording, 's' to stop recording, 'q' to quit: ").strip().lower()
            if cmd == 'r':
                loop_machine.start_recording()
            elif cmd == 's':
                loop_machine.stop_recording()
            elif cmd == 'q':
                loop_machine.stop()
                break
    except KeyboardInterrupt:
        loop_machine.stop()
