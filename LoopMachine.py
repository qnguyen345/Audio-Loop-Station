import sounddevice as sd
import numpy as np
import threading
import time

# Constants
CHUNK = 1024  # Frames per buffer
FORMAT = "int16"
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
BPM = 120  # User-defined tempo
BEATS_PER_LOOP = 4  # User-defined beats per loop
FRAMES_PER_LOOP = int((60 / BPM) * BEATS_PER_LOOP * RATE)  # Loop length in frames
ADJUSTMENT_FACTOR = 0.75  # Fine-tune latency correction

print(f"Loop duration: {FRAMES_PER_LOOP} samples ({BEATS_PER_LOOP} beats at {BPM} BPM)")

def generate_click(sample_rate=RATE, duration_ms=50, frequency=1000):
    """Generate a short click sound for the metronome."""
    duration_samples = int((duration_ms / 1000) * sample_rate)
    t = np.linspace(0, duration_ms / 1000, duration_samples, False)
    click = (np.sin(2 * np.pi * frequency * t) * 0.5 * 32767).astype(np.int16)
    return click.reshape(-1, 1)  # Ensure mono output

def generate_clicks():
    """Generate a full click track matching the loop length."""
    click = generate_click()
    silence = np.zeros((int((60 / BPM) * RATE) - len(click), 1), dtype=np.int16)
    return np.vstack([np.vstack((click, silence)) for _ in range(BEATS_PER_LOOP)])

class Track:
    def __init__(self, buffer, isMuted=False):
        self.buffer = buffer
        self.isMuted = isMuted

class LoopMachine:
    def __init__(self):
        # Allocate memory for multiple loop layers
        self.current_recording = None  # Active buffer being recorded
        self.tracks = []  # List of recorded tracks
        self.is_recording = False
        self.position = 0  # Playback and recording position
        self.click_track = generate_clicks()
        
        self.input_latency = sd.query_devices(kind='input')['default_low_input_latency']  # Cache latency
        self.latency_compensation_samples = int(self.input_latency * RATE * ADJUSTMENT_FACTOR)
        print(f"Measured Input Latency: {self.input_latency:.4f} sec, Compensation: {self.latency_compensation_samples} samples")
        
        self.stream = sd.Stream(
            samplerate=RATE,
            blocksize=CHUNK,
            channels=CHANNELS,
            dtype=FORMAT,
            callback=self.audio_callback
        )
        self.stream.start()

    def start_recording(self):
        """Start recording into a new buffer."""
        print("Recording started...")
        self.is_recording = True
        self.current_recording = np.zeros((FRAMES_PER_LOOP, CHANNELS), dtype=np.int16)

    def stop_recording(self):
        """Stop recording and store the completed segment with latency compensation."""
        print("Recording stopped.")
        self.is_recording = False
        if self.current_recording is not None:
            # Shift recording earlier while preserving full segment duration
            adjusted_recording = np.roll(self.current_recording, -self.latency_compensation_samples, axis=0)
            self.tracks.append(Track(adjusted_recording))
        self.current_recording = None

    def toggle_mute(self, track_index):
        """Toggle mute for a specific track."""
        if 0 <= track_index < len(self.tracks):
            self.tracks[track_index].isMuted = not self.tracks[track_index].isMuted
            status = "muted" if self.tracks[track_index].isMuted else "unmuted"
            print(f"Track {track_index} is now {status}.")

    def audio_callback(self, indata, outdata, frames, time, status):
        """Handles real-time recording and playback with latency compensation."""
        global_audio_out = np.zeros((frames, 1), dtype=np.int16)
        
        # Inject click track
        click_position = self.position % len(self.click_track)
        click_segment = self.click_track[click_position:click_position + frames]
        if click_segment.shape[0] < frames:
            padding = np.zeros((frames - click_segment.shape[0], 1), dtype=np.int16)
            click_segment = np.vstack((click_segment, padding))
        global_audio_out += click_segment
        
        # Record audio if recording is active
        if self.is_recording:
            start_idx = self.position
            end_idx = self.position + frames
            if end_idx >= FRAMES_PER_LOOP:
                first_part = indata[:FRAMES_PER_LOOP - start_idx]
                second_part = indata[FRAMES_PER_LOOP - start_idx:]
                self.current_recording[start_idx:] = first_part
                adjusted_recording = np.roll(self.current_recording, -self.latency_compensation_samples, axis=0)
                self.tracks.append(Track(adjusted_recording))
                self.current_recording = np.zeros((FRAMES_PER_LOOP, 1), dtype=np.int16)
                self.current_recording[:len(second_part)] = second_part
            else:
                self.current_recording[start_idx:end_idx] = indata
        
        for track in self.tracks:
            if not track.isMuted:
                playback_start = (self.position - self.latency_compensation_samples) % FRAMES_PER_LOOP
                loop_segment = track.buffer[playback_start:playback_start + frames]
                if loop_segment.shape[0] < frames:
                    padding = np.zeros((frames - loop_segment.shape[0], 1), dtype=np.int16)
                    loop_segment = np.vstack((loop_segment, padding))
                global_audio_out += loop_segment
        
        # Prevent clipping
        global_audio_out = np.clip(global_audio_out, -32768, 32767)
        outdata[:] = global_audio_out
        
        # Move position forward
        self.position += frames
        if self.position >= FRAMES_PER_LOOP:
            self.position = 0

    def stop(self):
        """Stops the loop machine and closes the audio stream."""
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

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