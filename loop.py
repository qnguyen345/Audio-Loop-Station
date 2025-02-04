from track import Track
import threading
import time
import sys

class Loop:
    def __init__(self, name, tempo, beats):
        self.name = name
        self.tempo = tempo  # Beats per minute
        self.beats = beats  # Number of beats in the loop
        self.loop_duration = (beats * 60) / tempo  # Loop duration in seconds
        self.tracks = []
        self.is_playing = False
        self.start_time = None
        self.track_threads = []  # To keep track of active track threads

    def play(self):
        if self.is_playing:
            print("Loop is already playing.")
            return

        self.is_playing = True
        self.start_time = time.perf_counter()
        print(f"Playback started. Loop duration: {self.loop_duration:.2f} seconds.")
        self._start_tracks()
        play_thread = threading.Thread(target=self._manage_playback, daemon=True)
        play_thread.start()

    def _start_tracks(self):
        """Ensure all tracks are started and playing in sync."""
        for track in self.tracks:
            if not track.get_muted():
                thread = threading.Thread(target=track.play, args=(0,), daemon=True)
                self.track_threads.append(thread)
                thread.start()

    def _manage_playback(self):
        while self.is_playing:
            current_time = time.perf_counter()
            elapsed_time = current_time - self.start_time
            playhead_position = elapsed_time % self.loop_duration  # Cyclical position

            print(f"Playhead position: {playhead_position:.2f} seconds")
            
            # Reset playhead for all tracks at the start of each loop
            if abs(playhead_position) < 0.01:  # Small tolerance for alignment
                with threading.Lock():
                    for track in self.tracks:
                        if not track.get_muted():
                            track.set_playhead(0)  # Reset playhead to start
            
            time.sleep(0.01)  # Polling interval to reduce CPU usage

    def stop(self):
        self.is_playing = False
        self.start_time = None
        for track in self.tracks:
            if not track.get_muted():
                track.stop()  # Ensure all tracks stop playing
        print("Playback stopped.")

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
        with threading.Lock():
            for track_id in ids:
                for track in self.tracks:
                    if track.get_uid() == track_id:
                        track._is_muted = False
                        print(f"Track {track_id} unmuted.")

    def mute_tracks(self, *ids):
        """Remove the specified tracks from playback."""
        with threading.Lock():
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
    loop = Loop("My First Loop", tempo=120, beats=4)
    loop.add_tracks(Track(5000, 1))  # Example track
    loop.play()

    print("Press any key to stop playback...")
    input()  # Wait for user input to stop playback

    loop.stop()
