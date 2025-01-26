# track.py
# Contains logic for audio streams and file handling

import pyaudio
import wave
import threading
import time
from datetime import datetime
from playsound import playsound
import random
import string
import json



class Track:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    RATE = 44100
    
    _filename: str
    _is_muted: bool
    _uid: str
    _custom_name: str
    _channels: int
    _duration: int
    _file_loaded: bool

    def __init__(self, duration, channels=1):
        """Create new Track object.
        
        Keyword arguments:
        duration -- length of loop in milliseconds 
        channels -- 1 for mono, 2 for stereo (default 1)
        """
        
        if channels not in [1, 2]:
            raise ValueError("Track must have 1 or 2 channels.")
                
        self._uid = ''.join(random.choices((string.ascii_letters + string.digits), k=12))
        self._filename = self._generate_filename()
        self._is_muted = False
        self._custom_name = ''
        self._channels = channels
        self._duration = duration
        self._file_loaded = False
        pass


    def _generate_filename(self, name=''):
        """Generate a filename with date, time, alphanumeric UID, and optional custom name.
        e.g., 2025-01-01T00:00:00Z_12345678_name.wav"""
        custom_name = f'_{name}' if name != '' else ''
        now = datetime.now()
        return f'{now.strftime("%Y-%m-%dT%H-%M-%S")}{custom_name}'


    def save_track(self):
        """Save the track object."""
        with open('tracks/saved_tracks.json', 'r') as file:
            tracks_index = json.load(file)
        tracks_index[self._uid] = self.__dict__
        with open('tracks/saved_tracks.json', 'w') as file:
            json.dump(tracks_index, file)
        pass
    
    def load_track(self, uid):
        pass
    
    def load_audio_file(self, filename):
        self._filename = filename
        self._file_loaded = True
        pass

    def play(self, start_position=0):
        """Plays the loaded audio file
        
        Keyword arguments:
        start_position -- playhead position in milliseconds (default 0)
        """
        if not self._file_loaded:
            raise AttributeError("Please record or load a file into the track before initiating playback.")

        # convert milliseconds to frames
        frame_position = int(self.RATE / 1000 * start_position)

        play_thread = threading.Thread(target=self._play_stream, daemon=True, args=(frame_position,))
        play_thread.start()

    def _play_stream(self, start_position):
        with wave.open(f'tracks/{self._filename}.wav') as wf:
            wf.setpos(start_position)            
            p=pyaudio.PyAudio()
            
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            print(f'Start playback of {self._filename}...')
            while len(data := wf.readframes(self.CHUNK)):
                stream.write(data)
            print('Playback complete.')
                
            stream.close()
            p.terminate()


    def stop():
        pass

    def record(self):
        rec_thread = threading.Thread(target=self._record_stream, daemon=True)
        rec_thread.start()
        self._file_loaded = True

    def _record_stream(self):
        with wave.open(f'tracks/{self._filename}.wav', 'wb') as wf:
            p = pyaudio.PyAudio()
            wf.setnchannels(self._channels)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            
            stream = p.open(format=self.FORMAT, channels=self._channels, rate=self.RATE, input=True)
            print('Recording...')
            # for chunk in range(0, self.RATE // self.CHUNK * (self._duration // 1000)):
            #     wf.writeframes(stream.read(self.CHUNK))
            start_time = time.time()
            while True:
                wf.writeframes(stream.read(self.CHUNK))
                if (time.time() - start_time) * 1000 >= self._duration:
                    break
            
            
            print('Done')
            
            stream.close()
            p.terminate()
    
    
    # def rename(name):
    #     pass
    

if __name__ == "__main__":
    def debug_timer(duration):
        for sec in range((duration // 1000) + 1, 0, -1):
            print(sec)
            time.sleep(1)
    
    test_duration = 1000
    
    new_track = Track(test_duration)
    print(new_track._filename)
    new_track.record()
    debug_timer(test_duration)
    
    new_track.play()
    debug_timer(test_duration)
    
    new_track.save_track()
    pass