from track import Track
import threading
import time

# Notes
# - Metronome

class Loop:
    def __init__(self, name):
        self.name = name
        self.is_playing = False
        self.tracks = []
        self.playhead_position = 0
        self.lock = threading.Lock()

    def play(self):
        """Start playback, beginning from the current playhead position."""
        if self.is_playing:
            print("Playback is already running.")
            return

        self.is_playing = True
        play_thread = threading.Thread(target=self._play_tracks, daemon=True)
        play_thread.start()

    def _play_tracks(self):
        while self.is_playing:
            with self.lock:
                for track in self.tracks:
                    if not track.get_muted():
                        track.play(self.playhead_position)
            time.sleep(0.1)  # Allow for thread context switching

    def pause(self):
        """Pause playback, keeping the playhead where it is."""
        self.is_playing = False
        print("Playback paused.")

    def stop(self):
        """Stop playback and reset the playhead to 0."""
        self.is_playing = False
        self.playhead_position = 0
        print("Playback stopped and playhead reset.")

    def record(self, duration, channels=1):
        """Begin recording a new track."""
        new_track = Track(duration, channels)
        new_track.record()
        self.tracks.append(new_track)
        print(f"New track recorded and added to loop: {new_track.get_uid()}.")

    def stop_recording(self):
        """Stop recording, and discard the currently unfinished track."""
        if self.tracks and not self.tracks[-1].get_audio_file_loaded():
            self.tracks.pop()
            print("Recording stopped and unfinished track discarded.")
        else:
            print("No recording in progress to stop.")

    def unmute_tracks(self, *ids):
        """Add the specified tracks to playback."""
        with self.lock:
            for track_id in ids:
                for track in self.tracks:
                    if track.get_uid() == track_id:
                        track._is_muted = False
                        print(f"Track {track_id} unmuted.")

    def mute_tracks(self, *ids):
        """Remove the specified tracks from playback."""
        with self.lock:
            for track_id in ids:
                for track in self.tracks:
                    if track.get_uid() == track_id:
                        track._is_muted = True
                        print(f"Track {track_id} muted.")

    def add_tracks(self, *tracks):
        """Add tracks to the loop."""
        for track in tracks:
            if isinstance(track, Track):
                self.tracks.append(track)
                print(f"Track {track.get_uid()} added to loop.")

    def remove_tracks(self, *ids):
        """Remove tracks from the loop."""
        self.tracks = [track for track in self.tracks if track.get_uid() not in ids]
        print(f"Tracks {', '.join(ids)} removed from loop.")

    def rename(self, new_name):
        """Rename the loop."""
        self.name = new_name
        print(f"Loop renamed to {new_name}.")

if __name__ == "__main__":
    loop = Loop("My First Loop")
    loop.record(5000)
    time.sleep(6)
    loop.play()
    time.sleep(5)
    loop.pause()
    loop.rename("My Renamed Loop")
    loop.stop()
