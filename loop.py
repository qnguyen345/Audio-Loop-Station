import time
from track import Track

class Loop:
    def __init__(self, tempo, duration):
        """
        Initialize a loop with the specified tempo (BPM) and duration (in seconds).

        Args:
            tempo (int): Tempo in beats per minute.
            duration (int): Duration of the loop in seconds.
        """
        self.tempo = tempo
        self.duration = duration
        self.tracks = []  # List to hold tracks within this loop
        self.is_recording = False
        self.is_playing = False
        self.playback_position = 0  # Current position in playback

    def add_track(self, track):
        """
        Add a track to the loop.

        Args:
            track (Track): The track object to add.
        """
        self.tracks.append(track)

    def start_recording(self):
        """Start recording a new track."""
        if self.is_recording:
            return

        self.is_recording = True
        self.is_playing = False
        print("Recording started.")

    def stop_recording(self):
        """Stop recording the current track."""
        if not self.is_recording:
            return

        self.is_recording = False
        self.is_playing = True
        print("Recording stopped. Track saved.")

    def play(self):
        """Start or resume playback of the loop."""
        if self.is_playing:
            return

        self.is_playing = True
        print("Playback started.")

    def stop(self):
        """Stop playback of the loop."""
        if not self.is_playing:
            return

        self.is_playing = False
        print("Playback stopped.")

    def trim_loop(self):
        """Trim all tracks in the loop to match the loop's start and end points."""
        for track in self.tracks:
            track.trim(self.duration)
        print("Loop trimmed to match duration.")

    def save_loop(self, filepath):
        """
        Save the loop to a file for later access.

        Args:
            filepath (str): The path to save the loop file.
        """
        # Logic to combine tracks and save them as a single file
        print(f"Loop saved to {filepath}.")

    def load_loop(self, filepath):
        """
        Load a previously saved loop from a file.

        Args:
            filepath (str): The path to the loop file to load.
        """
        # Logic to load loop from file
        print(f"Loop loaded from {filepath}.")

    def __repr__(self):
        track_details = "\n".join([f"  - {track}" for track in self.tracks])
        return (
            f"<Loop tempo={self.tempo} duration={self.duration} tracks={len(self.tracks)}>\n"
            f"Tracks:\n{track_details}"
        )

if __name__ == "__main__":
    loop = Loop(tempo=120, duration=8)
    print(loop)

    loop.add_track(Track())
    loop.add_track(Track())
    loop.add_track(Track())
    print(loop)

    # time.sleep(2)  # Wait for 2 seconds to simulate recording time

    # loop.stop_recording()
