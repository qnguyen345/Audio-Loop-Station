import copy
import dill as pickle
from datetime import datetime
import librosa
import numpy as np
import os
import sounddevice as sd
import shlex
import threading
import uuid

# Constants
CHUNK = 1024  # Frames per buffer
FORMAT = "int16"
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
# BPM = 120  # User-defined tempo
# BEATS_PER_LOOP = 4  # User-defined beats per loop
# FRAMES_PER_LOOP = int((60 / BPM) * BEATS_PER_LOOP * RATE)  # Loop length in frames
ADJUSTMENT_FACTOR = 0.75  # Fine-tune latency correction

# print(f"Loop duration: {FRAMES_PER_LOOP} samples ({BEATS_PER_LOOP} beats at {BPM} BPM)")

FIRST_CLICK_FREQ = 1500  # Frequency (Hz) for the first beat’s click
REGULAR_CLICK_FREQ = 1000  # Frequency (Hz) for the rest of the clicks

def generate_click(sample_rate=RATE, duration_ms=50, *, frequency):
    """Generate a short click sound for the metronome."""
    duration_samples = int((duration_ms / 1000) * sample_rate)
    t = np.linspace(0, duration_ms / 1000, duration_samples, False)
    click = (np.sin(2 * np.pi * frequency * t) * 0.5 * 32767).astype(np.int16)
    return click.reshape(-1, 1)  # Ensure mono output

def generate_clicks(bpm: int, beats_per_loop: int):
    """Generate a full click track matching the loop length, with the first click pitched differently."""
    samples_per_beat = int((60 / bpm) * RATE)
    
    # Generate the first click using a different frequency.
    first_click = generate_click(frequency=FIRST_CLICK_FREQ)
    first_silence = np.zeros((samples_per_beat - len(first_click), 1), dtype=np.int16)
    first_segment = np.vstack((first_click, first_silence))
    
    # Generate the regular click for the other beats.
    regular_click = generate_click(frequency=REGULAR_CLICK_FREQ)
    regular_silence = np.zeros((samples_per_beat - len(regular_click), 1), dtype=np.int16)
    regular_segment = np.vstack((regular_click, regular_silence))
    
    # Build the full click track: first beat is first_segment; remaining beats use regular_segment.
    segments = [first_segment] + [regular_segment for _ in range(beats_per_loop - 1)]
    return np.vstack(segments)

class Track:
    def __init__(self, frames_per_loop: int):
        self.frames_per_loop = frames_per_loop
        self.raw_buffer = np.zeros((self.frames_per_loop, CHANNELS), dtype=np.int16)
        self.buffer = self.raw_buffer
        self.is_muted = False
        self.pitch_shift = 0
        self.name = None
        self.is_recording = False
        self.track_uid = uuid.uuid4()

    def apply_pitch_shift_async(self):
        """Offload pitch shifting to a background thread and update immediately when done."""
        def worker():
            if self.pitch_shift == 0:
                # No pitch shift needed; just copy the raw buffer.
                self.buffer = self.raw_buffer.copy()
            else:
                # Normalize and perform pitch shifting.
                buffer_float = self.raw_buffer.astype(np.float32) / 32767.0  # Normalize to [-1, 1]
                buffer_shifted = librosa.effects.pitch_shift(
                    buffer_float.flatten(), sr=RATE, n_steps=self.pitch_shift
                )
                self.buffer = (np.clip(buffer_shifted, -1, 1) * 32767).astype(np.int16).reshape(-1, 1)

        threading.Thread(target=worker, daemon=True).start()

    def __str__(self):
        elements = []

        elements.append(self.name or "Untitled")

        if self.is_muted:
            elements.append("M")

        if self.pitch_shift > 0:
            elements.append("+" + str(self.pitch_shift))
        elif self.pitch_shift < 0:
            elements.append(str(self.pitch_shift))

        return "<" + " ".join(elements) + ">"

class LoopMachine:
    def __init__(self, bpm: int, beats_per_loop: int):
        # Allocate memory for multiple loop layers
        self.bpm = bpm
        self.beats_per_loop = beats_per_loop
        self.frames_per_loop = int((60 / self.bpm) * self.beats_per_loop * RATE)  # Loop length in frames
        self.current_track = None  # Active buffer being recorded
        self.tracks = []  # List of recorded tracks
        # self.is_recording = False
        self.position = 0  # Playback and recording position
        self.checkpoint_position = 0
        self.checkpoint_action = None # Action to perform on reaching checkpoint
        self.click_track = generate_clicks(self.bpm, self.beats_per_loop)
        self.click_is_muted = True
        self.uid = uuid.uuid4()
        self.time = f'{datetime.now().strftime("%Y-%m-%d-T%H-%M-%S")}'
        self.is_playing= True
     
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
        self._prewarm()

    def start_recording(self):
        """Start recording into a new buffer."""
        print("Recording started...")
        self._set_checkpoint_now()
        self.checkpoint_action = "NEW"
        self.click_is_muted = False
        
    def stop_recording(self):
        """Stop recording and store the completed segment with latency compensation."""
        print("Recording stopped.")
        self._set_checkpoint_now()
        self.checkpoint_action = "STOP"

    def _set_checkpoint_now(self):
        self.checkpoint_position = (self.position + self.latency_compensation_samples) % self.frames_per_loop

    def audio_callback(self, indata, outdata, frames, time, status):
        """Handles real-time recording and playback with latency compensation."""
        global_audio_out = np.zeros((frames, 1), dtype=np.int16)
        # If paused, return nothing
        if not self.is_playing:  
            outdata[:] = global_audio_out
            return
        # Handle checkpoint
        start = self.position
        end = (self.position + frames) % self.frames_per_loop
        if start < end:
            checkpoint_reached = (start <= self.checkpoint_position < end)
        else:
            checkpoint_reached = (self.checkpoint_position >= start or self.checkpoint_position < end)
        if checkpoint_reached:
            if self.checkpoint_action in ("STOP", "NEW"):
                if self.current_track:
                    self.current_track.is_recording = False
                    self.current_track = None
            if self.checkpoint_action == "NEW":
                new_track = Track(self.frames_per_loop)
                new_track.is_recording = True
                self.current_track = new_track
                self.tracks.append(new_track)
            self.checkpoint_action = None

        # Record audio if recording is active
        if self.current_track:
            start_idx = self.position
            end_idx = self.position + frames
            if end_idx > self.frames_per_loop:
                # Calculate how many samples can be written before reaching the end.
                samples_until_end = self.frames_per_loop - start_idx
                # Write the first part into the end of the buffer.
                self.current_track.raw_buffer[start_idx:] = indata[:samples_until_end]
                # Write the remaining samples at the beginning of the buffer.
                remaining_samples = frames - samples_until_end
                self.current_track.raw_buffer[:remaining_samples] = indata[samples_until_end:]
            else:
                self.current_track.raw_buffer[start_idx:end_idx] = indata
        
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
            if not track.is_muted and not track.is_recording:
                playback_start = (self.position + self.latency_compensation_samples) % self.frames_per_loop
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
        if self.position >= self.frames_per_loop:
            self.position = 0
    
    def stop(self):
        """Stops the loop machine and closes the audio stream."""
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

    def _prewarm(self):
        def worker():
            dummy_buffer = np.zeros(RATE, dtype=np.float32)
            _ = librosa.effects.pitch_shift(dummy_buffer, sr=RATE, n_steps=1)

        threading.Thread(target=worker, daemon=True).start()

    def __getstate__(self):
        # Pickle uses this dunder method to access object data
        state = self.__dict__.copy()
        state['stream'] = None
        return state

    def save(self, loop_name:str=''):
        """Saves the loop as a Pickle, includes any linked Track objects.

        Ignores the stream to prevent need to close stream
        """

        # date-time-uid-loopname.pkl:
        if loop_name:
            loop_name = f'_{loop_name}'
        filename = f'{self.time}-{self.uid}{loop_name}.pkl'
        with open(os.path.join('loops', filename), 'wb') as file:
            pickle.dump(self, file)
            
    def load(self, filename: str):
        """Loads a saved loop object using the filename.
        
        Waits until end of loop to complete load
        Keeps stream open and replaces the list of tracks, and some other info
        Ignores loaded file's click status
        
        Keyword arguments:
        filename -- example: "2025-02-08-T15-44-20-CxilTDgH.pkl"
        """ 
        try:
            with open(os.path.join('loops', filename), 'rb') as file:
                loaded = pickle.load(file)
                # adjust while current loop is finishing
                loaded.__dict__['click_is_muted'] = self.click_is_muted
                loaded.__dict__['stream'] = self.stream
                loaded.position = 0
                while self.position > 0:
                    continue
                # O(1):
                self.__dict__ = loaded.__dict__

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
    tempo = int(input('Tempo: '))
    beats = int(input('Beats per Loop: '))
    loop_machine = LoopMachine(tempo, beats)
    print("== LoopMachine ==")
    print(f"Loop duration: {loop_machine.frames_per_loop} samples ({loop_machine.beats_per_loop} beats at {loop_machine.bpm} BPM)")
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
h           help
l           list tracks
la <FLOAT>  set latency samples (seconds)
m/u <i>     mute/unmute track by index
n <i>       set name for track by index
p <i> <INT> set pitch shift for track by index
q           quit
r           start recording
s           stop recording
y <i>       copy track by index
yy          copy the most recent track
save <n>    save the loop machine object with optional name <n>
load <f>    load a loop machine object with filename <f> 
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
            elif cmd == 'l':
                print(loop_machine)
            elif cmd.startswith('la'):
                new_latency = int(float(args[-1]) * RATE)
                print(f"Setting latency to {new_latency}...")
                loop_machine.latency_compensation_samples = new_latency
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
                track.apply_pitch_shift_async()
            elif cmd == 'yy':
                track_index = -1
                track = loop_machine.tracks[track_index]
                loop_machine.tracks.append(copy.copy(track))
            elif cmd.startswith('y'):
                track_index = int(args[1])
                track = loop_machine.tracks[track_index]
                loop_machine.tracks.append(copy.copy(track))
            elif cmd.startswith('save'):
                args = shlex.split(cmd)
                if len(args) == 1:
                    loop_machine.save()
                elif len(args) == 2:
                    loop_machine.save(args[1])
            elif cmd.startswith('load'):
                loop_machine.load(args[1])
                print(loop_machine)
            elif cmd == 'repr':
                loop_machine.repr_log()
                print(repr(loop_machine))
                
    except KeyboardInterrupt:
        loop_machine.stop()
