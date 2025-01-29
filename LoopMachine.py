import pyaudio
import numpy as np
import threading
import time

# Constants
CHUNK = 1024  # Frames per buffer
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
LOOP_DURATION_SEC = 4  # Define loop length (adjustable)
FRAMES_PER_LOOP = RATE * LOOP_DURATION_SEC  # Number of samples in one loop

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
        self.is_recording = True
        self.current_recording = np.zeros((FRAMES_PER_LOOP, CHANNELS), dtype=np.int16)
        self.recording_index = len(self.loops)  # New segment
        print("Recording started...")

    def stop_recording(self):
        """Stop recording and discard the current incomplete segment."""
        self.is_recording = False
        self.current_recording = None
        print("Recording stopped.")

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback function for handling synchronized recording and playback."""
        # Allocate memory for output stream
        global_audio_out = np.zeros((frame_count, CHANNELS), dtype=np.int16)

        # Read from input stream

        if self.is_recording:
            if in_data is None:
                print("Warning: No input data received!")
                # return (b'\x00' * frame_count * 2, pyaudio.paContinue)  # Return silence
            input_audio = np.frombuffer(in_data, dtype=np.int16).reshape(-1, CHANNELS)

            # Write incoming audio to the recording buffer
            start_idx = self.position
            end_idx = self.position + frame_count

            if end_idx >= FRAMES_PER_LOOP:
                # Wrap around if we reach the end of the loop
                first_part = input_audio[:FRAMES_PER_LOOP - start_idx]
                second_part = input_audio[FRAMES_PER_LOOP - start_idx:]

                self.current_recording[start_idx:] = first_part
                self.loops.append(self.current_recording)  # Save completed segment

                # Start a new segment
                self.current_recording = np.zeros((FRAMES_PER_LOOP, CHANNELS), dtype=np.int16)
                self.current_recording[:len(second_part)] = second_part
            else:
                # Fill the current recording segment
                self.current_recording[start_idx:end_idx] = input_audio

        # Mix playback audio from recorded loops
        for loop in self.loops:
            global_audio_out += loop[self.position:self.position + frame_count]

        # Prevent clipping
        global_audio_out = np.clip(global_audio_out, -32768, 32767)

        # Move forward in the loop buffer
        self.position += frame_count
        if self.position >= FRAMES_PER_LOOP:
            self.position = 0  # Wrap around to the start of the loop

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
