import sounddevice as sd
import numpy as np
import queue
import threading

class LoopMachine:
    def __init__(self, bpm=120, beats_per_loop=4, sample_rate=44100, channels=1):
        self.bpm = bpm
        self.beats_per_loop = beats_per_loop
        self.sample_rate = sample_rate
        self.channels = channels
        self.loop_duration = (60 / self.bpm) * self.beats_per_loop
        self.buffer_size = int(self.loop_duration * self.sample_rate)
        self.buffer = np.zeros((self.buffer_size, self.channels), dtype=np.float32)
        self.track_queue = queue.Queue()
        self.recording = False
        self.playing = False
        self.thread = None

    def generate_click_track(self):
        click_freq = 1000  # Hz
        click_duration = 0.02  # seconds
        silence_duration = (60 / self.bpm) - click_duration
        click_samples = int(click_duration * self.sample_rate)
        silence_samples = int(silence_duration * self.sample_rate)
        click_wave = np.sin(2 * np.pi * np.linspace(0, click_freq, click_samples))
        silence_wave = np.zeros(silence_samples)
        return np.concatenate((click_wave, silence_wave))
    
    def audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        if self.recording:
            self.buffer[:frames] = indata[:frames]
        if self.playing:
            outdata[:] = self.buffer[:frames]
        else:
            outdata.fill(0)
    
    def start_recording(self):
        self.recording = True
        self.playing = True
        self.thread = threading.Thread(target=self.process_audio)
        self.thread.start()
    
    def stop_recording(self):
        self.recording = False
    
    def start_playback(self):
        self.playing = True
    
    def stop_playback(self):
        self.playing = False
    
    def process_audio(self):
        with sd.Stream(samplerate=self.sample_rate, channels=self.channels,
                       callback=self.audio_callback, dtype=np.float32):
            while self.recording or self.playing:
                sd.sleep(100)
    
if __name__ == "__main__":
    loop_machine = LoopMachine(bpm=120, beats_per_loop=4)
    print("Commands: [r] Start/Stop Recording, [p] Start/Stop Playback, [q] Quit")
    
    while True:
        command = input("Enter command: ").strip().lower()
        if command == 'r':
            if loop_machine.recording:
                loop_machine.stop_recording()
                print("Recording stopped.")
            else:
                loop_machine.start_recording()
                print("Recording started.")
        elif command == 'p':
            if loop_machine.playing:
                loop_machine.stop_playback()
                print("Playback stopped.")
            else:
                loop_machine.start_playback()
                print("Playback started.")
        elif command == 'q':
            print("Exiting...")
            exit(0)
