import copy
import dill as pickle
from datetime import datetime
import librosa
import numpy as np
import os
import sounddevice as sd
import random
import string
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
    def __init__(self, raw_buffer, is_muted=False, pitch_shift=0):
        self.raw_buffer = raw_buffer
        self.is_muted = is_muted
        self.pitch_shift = pitch_shift
        self.name = None
        self.apply_pitch_shift()

    def apply_pitch_shift(self):
        """Applies pitch shifting to the track buffer."""
        if self.pitch_shift == 0:
            self.buffer = self.raw_buffer
        else:
            buffer_float = self.raw_buffer.astype(np.float32) / 32767.0  # Normalize to [-1,1]
            buffer_shifted = librosa.effects.pitch_shift(buffer_float.flatten(), sr=RATE, n_steps=self.pitch_shift)
            self.buffer = (np.clip(buffer_shifted, -1, 1) * 32767).astype(np.int16).reshape(-1, 1)

    def __str__(self):
        elements = []

        elements.append(self.name or "Untitled")

        if self.is_muted:
            elements.append("M")

        if self.pitch_shift > 0:
            elements.append("+" + str(self.pitch_shift))
        elif self.pitch_shift < 0:
            elements.append(self.pitch_shift)

        return "<" + " ".join(elements) + ">"

class LoopMachine:
    def __init__(self):
        # Allocate memory for multiple loop layers
        self.current_recording = None  # Active buffer being recorded
        self.tracks = []  # List of recorded tracks
        self.is_recording = False
        self.position = 0  # Playback and recording position
        self.click_track = generate_clicks()
        self.click_is_muted = True # Mute click when app initially starts
        self.uid = ''.join(random.choices((string.ascii_letters + string.digits), k=8))
        self.time = f'{datetime.now().strftime("%Y-%m-%d-T%H-%M-%S")}'
        
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
        self.click_is_muted = False
        return self.uid
        
    def stop_recording(self):
        """Stop recording and store the completed segment with latency compensation."""
        print("Recording stopped.")
        self.is_recording = False
        if self.current_recording is not None:
            # Shift recording earlier while preserving full segment duration
            adjusted_recording = np.roll(self.current_recording, -self.latency_compensation_samples, axis=0)
            self.tracks.append(Track(adjusted_recording))
        self.current_recording = None

    def audio_callback(self, indata, outdata, frames, time, status):
        """Handles real-time recording and playback with latency compensation."""
        global_audio_out = np.zeros((frames, 1), dtype=np.int16)
        
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
        
        # Inject click track
        if not self.click_is_muted:
            click_position = self.position % len(self.click_track)
            click_segment = self.click_track[click_position:click_position + frames]
            if click_segment.shape[0] < frames:
                padding = np.zeros((frames - click_segment.shape[0], 1), dtype=np.int16)
                click_segment = np.vstack((click_segment, padding))
            global_audio_out += click_segment
        
        # Inject tracks
        for track in self.tracks:
            if not track.is_muted:
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

    def save(self):
        """Saves the loop as a Pickle, includes any linked Track objects."""
        # safely close the stream:
        self.stop()
        
        # Pickling is unable to process some C-type objects
        # prevents TypeError: cannot pickle '_cffi_backend.__CDataOwnGC' object
        self.stream = None
        
        # date-time-uid.pkl:
        filename = f'{self.time}-{self.uid}.pkl'
        with open(os.path.join('loops', filename), 'wb') as file:
            pickle.dump(self, file)
            
        # reinitialize the stream:
        self.stream = sd.Stream(
            samplerate=RATE,
            blocksize=CHUNK,
            channels=CHANNELS,
            dtype=FORMAT,
            callback=self.audio_callback
        )
        self.stream.start()
        
    @classmethod    
    def load(cls, filename: str, close_loop=None):
        """Loads a saved loop object using the filename
        
        Keyword arguments:
        filename -- example: "2025-02-08-T15-44-20-CxilTDgH.pkl"
        close_loop -- include an existing loop object to close its stream
        """ 
        if close_loop:
            close_loop.stop()
        
        try:
            with open(os.path.join('loops', filename), 'rb') as file:
                loaded = pickle.load(file)
                loaded.stream = sd.Stream(
                    samplerate=RATE,
                    blocksize=CHUNK,
                    channels=CHANNELS,
                    dtype=FORMAT,
                    callback=loaded.audio_callback
                )
                loaded.stream.start()
                return loaded
        except FileNotFoundError:
            print(f'{filename} was not found.')

    def repr_log(self):
        with open('repr_log.txt', 'a') as log:
            log.write('\n')
            log.write('___________________\n')
            log.write(f'{self.__class__.__name__}: \n')
            for key in self.__dict__:
                log.write(f'{key}: {self.__dict__[key]} \n')

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.__dict__}'

    def __str__(self):
        result = f"Tracks ({len(self.tracks)}):"
        for i, track in enumerate(self.tracks):
            result += f"\n  {i}: {track}"
        return result
    
if __name__ == "__main__":
    loop_machine = LoopMachine()
    print("== LoopMachine ==")
    try:
        while True:
            cmd = input("> ").strip()
            args = cmd.split()
            if cmd == 'h':
                help_text = """-----------------------------------------------------------------------------------------------------------------------
== LoopMachine ==

c           toggle click track
d <i>       delete track by index
dd          delete the most recent track
i           info
h           help
m/u <i>     mute/unmute track by index
n <i>       set name for track by index
p <i>       set pitch shift for track by index
q           quit
r           start recording
s           stop recording
y <i>       copy track by index
yy          copy the most recent track
save        save the loop machine object
load <f><l> load a loop machine object with filename <f>; close currently loaded loop <l> (optional) 
repr        print a dictionary representation of the loop
-----------------------------------------------------------------------------------------------------------------------"""
                print(help_text)
            elif cmd == 'c':
                loop_machine.click_is_muted = not loop_machine.click_is_muted
            elif cmd == 'dd':
                loop_machine.tracks.pop()
            elif cmd.startswith('d'):
                track_index = int(args[-1])
                loop_machine.tracks.pop(track_index)
            elif cmd == 'i':
                print(loop_machine)
            elif cmd.startswith('m') or cmd.startswith('u'):
                track_index = int(args[-1])
                track = loop_machine.tracks[track_index]
                track.is_muted = cmd.startswith('m')
            elif cmd.startswith('n'):
                track_index = int(args[1])
                name = args[2]
                track = loop_machine.tracks[track_index]
                track.name = name
            elif cmd == 'q':
                loop_machine.stop()
                break
            elif cmd == 'r':
                loop_machine.start_recording()
            elif cmd == 's':
                loop_machine.stop_recording()
            elif cmd.startswith('p'):
                track_index = int(args[1])
                pitch_shift = int(args[2])
                track = loop_machine.tracks[track_index]
                track.pitch_shift = pitch_shift
                track.apply_pitch_shift()
            elif cmd == 'yy':
                track_index = -1
                track = loop_machine.tracks[track_index]
                loop_machine.tracks.append(copy.copy(track))
            elif cmd.startswith('y'):
                track_index = int(args[1])
                track = loop_machine.tracks[track_index]
                loop_machine.tracks.append(copy.copy(track))
            elif cmd.startswith('save'):
                loop_machine.save()
            elif cmd.startswith('load'):
                loop_machine = LoopMachine.load(args[1], loop_machine)
                print(loop_machine)
            elif cmd == 'repr':
                loop_machine.repr_log()
                print(repr(loop_machine))
                
    except KeyboardInterrupt:
        loop_machine.stop()
