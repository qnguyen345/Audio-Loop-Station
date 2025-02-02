# track.py
# Contains logic for audio streams and file handling
#
#
# Track() object represents a track that can be linked to an existing wav file,
# or it can record a new wav file that is automatically linked.
#
# To use module:
#   "from track import Track"
# To create a track:
#   "track1 = Track(5000, 1)""

# -------- Please run in a Python 3.11 virtual environment -------- #


from datetime import datetime
import json
import os
import pyaudio
import random
import string
import threading
import time
import wave


class Track:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    RATE = 44100

    _filename: str
    _custom_name: str
    _uid: str
    _channels: int
    _duration: int
    _is_muted: bool
    _file_loaded: bool
    _is_playing: bool

    _stream: object

    def __init__(self, duration=0, channels=1):
        """Create new Track object; no audio file loaded on init.

        Keyword arguments:
        duration -- length of loop in milliseconds 
        channels -- 1 for mono, 2 for stereo (default 1)

        Implementation notes: 
        Recording a mono audio feed to a stereo track doesn't work and is not handled yet.
        """

        if channels not in [1, 2]:
            raise ValueError("Track must have 1 or 2 channels.")

        self._uid = ''.join(random.choices(
            (string.ascii_letters + string.digits), k=12))
        self._filename = self._generate_filename()
        self._custom_name = ''
        self._channels = channels
        self._duration = duration
        self._is_muted = False
        self._file_loaded = False
        self._is_playing = False

    def save_track(self):
        """Save the track object data to tracks/saved_tracks.json."""
        with open('tracks/saved_tracks.json', 'r') as file:
            tracks_index = json.load(file)
        tracks_index[self._uid] = self.__dict__
        with open('tracks/saved_tracks.json', 'w') as file:
            json.dump(tracks_index, file)

    def load_track(self, uid=''):
        """Load a saved track; if no UID provided, lists saved tracks.

        Keywork arguments:
        uid -- string (default='')"""
        if uid == '':
            print("Saved Tracks:")
            with open('tracks/saved_tracks.json', 'r') as file:
                saved_tracks = json.load(file)
                for track in saved_tracks:
                    print(
                        f"Track ID: {track} | Audio File: {saved_tracks[track]['_filename']}.wav")
                return saved_tracks
        else:
            try:
                with open('tracks/saved_tracks.json', 'r') as saved_tracks:
                    tracks = json.load(saved_tracks)
                    self._uid = tracks[uid]['_uid']
                    self._filename = tracks[uid]['_filename']
                    self._is_muted = tracks[uid]['_is_muted']
                    self._custom_name = tracks[uid]['_custom_name']
                    self._channels = tracks[uid]['_channels']
                    self._duration = tracks[uid]['_duration']
                    self._file_loaded = tracks[uid]['_file_loaded']
                    self._is_playing = False
            except:
                raise KeyError(f"Track UID {uid} does not exist.")

    def load_audio_file(self, filename=''):
        """Load an existing audio file into the track; if no filename provided, lists all audio files.

        Keywork arguments:
        filename -- string (default='')
        """
        files = os.listdir('tracks/')
        files.sort()
        if filename == '':
            for file in files:
                if file.endswith('wav'):
                    print(file)
        elif filename in files:
            self._filename = filename[0:-4]
            self._file_loaded = True
            with wave.open(f'tracks/{filename}') as wf:
                self._channels = wf.getnchannels()
                frames = wf.getnframes()
                self._duration = (frames // self.RATE) * 1000

        else:
            raise OSError(f"Audio file {filename} not found")

    def play(self, start_position=0):
        """Plays the loaded audio file in a thread, repeating until Track.stop() is called.

        Keyword arguments:
        start_position -- playhead position in milliseconds (default 0)
            Playback repeats from this position as well

        Implementation notes:
        start_position would shorten the length of the file, unsyncing from other loops.
        I may need to add an equal amount of time to the end.
        """
        if not self._file_loaded:
            raise AttributeError(
                "Please record or load a file into the track before initiating playback.")

        # convert milliseconds to frames
        frame_position = int(self.RATE / 1000 * start_position)

        play_thread = threading.Thread(
            target=self._play_stream, daemon=True, args=(frame_position,))
        play_thread.start()

    def _play_stream(self, start_position):
        """Helper method for play()"""
        with wave.open(f'tracks/{self._filename}.wav') as wf:
            wf.setpos(start_position)
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            print(f'Start playback of {self._filename}...')
            self._is_playing = True
            while self._is_playing:
                while len(data := wf.readframes(self.CHUNK)):
                    stream.write(data)
                wf.setpos(start_position)
            print('Playback complete.')

            stream.close()
            p.terminate()

    def stop(self):
        """ Breaks the playback loop, which closes the thread """
        self._is_playing = False

    def record(self):
        """ Starts recording for track's duration """
        rec_thread = threading.Thread(target=self._record_stream, daemon=True)
        rec_thread.start()

    def _record_stream(self):
        """helper method for record()"""
        with wave.open(f'tracks/{self._filename}.wav', 'wb') as wf:
            p = pyaudio.PyAudio()
            wf.setnchannels(self._channels)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)

            stream = p.open(format=self.FORMAT,
                            channels=self._channels, rate=self.RATE, input=True)

            print('Recording...')
            start_time = time.time()
            while True:
                wf.writeframes(stream.read(self.CHUNK))
                if (time.time() - start_time) * 1000 >= self._duration:
                    break
            print('Done')

            stream.close()
            p.terminate()
            self._file_loaded = True

    def rename(self, name: str = ''):
        """Updates the track's custom name and the filename, if a file is loaded.
        """
        self._custom_name = name
        new_filename = f'{self._filename}_{name}'
        if self._file_loaded:
            wav_file = os.path.join('tracks', f'{self._filename}.wav')
            wav_file_new_name = os.path.join('tracks', f'{new_filename}.wav')
            os.rename(wav_file, wav_file_new_name)
        self._filename = new_filename
        print(f'Track renamed to {name}.')

    def _generate_filename(self, name=''):
        """Generate a filename with date, time.
        e.g., 2025-01-01T00:00:00Z.wav
        """
        custom_name = f'_{name}' if name != '' else ''
        now = datetime.now()
        return f'{now.strftime("%Y-%m-%dT%H:%M:%S")}{custom_name}'

    #####################
    #      GETTERS      #
    #####################
    def get_uid(self):
        return self._uid

    def get_custom_name(self):
        return self._custom_name

    def get_filename(self):
        return f'{self._filename}.wav'

    def get_muted(self):
        return self._is_muted

    def get_channels(self):
        return self._channels

    def get_duration(self):
        return self._duration

    def get_audio_file_loaded(self):
        return self.get_audio_file_loaded

    #####################
    #      SETTERS      #
    #####################
    def set_duration(self, duration: int):
        """Set track duration in milliseconds"""
        self._duration = duration

    #####################
    #      UTILITY      #
    #####################

    def __str__(self):
        """print(some_track) to display track data."""
        return (f'''
               --- TRACK DATA ---
               Track UID: {self._uid}
               Custom Name: {self._custom_name}
               Filename: {self._filename}
               Muted: {self._is_muted}
               Channels: {self._channels}
               Duration: {self._duration}
               Audio File Loaded: {self._file_loaded}
               ''')


if __name__ == "__main__":
    def debug_timer(duration):
        for sec in range((duration // 1000) + 1, 0, -1):
            print(sec)
            time.sleep(1)

    test_duration = 1000

    new_track = Track(test_duration)
    new_track.record()
    print(new_track)
    new_track.rename('new_name')

    # new_track.record()
    # debug_timer(test_duration)

    # new_track.play()
    # debug_timer(test_duration)

    # new_track.save_track()

    # new_track.load_track()
    # new_track.load_track('uveGSSfHBTqK')
    # new_track.load_audio_file()
    print(new_track)
    pass
