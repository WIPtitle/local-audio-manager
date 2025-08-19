from pathlib import Path
from app.jobs.audio_manager import AudioManager
from app.clients.audio_server_client import AudioServerClient


class AudioManagerImpl(AudioManager):
    def __init__(self, audio_client: AudioServerClient):
        self.audio_client = audio_client
        self.running = False
        self.current_audio_name = None

    def start_audio(self, path):
        """Start playing an audio file

        Args:
            path: Can be a string path or Path object to the audio file
        """
        # Convert to Path object if string
        if isinstance(path, (str, Path)):
            path = Path(path)
            # Get full filename with extension
            audio_name = path.name

            # Only restart if it's a different audio
            if self.current_audio_name != audio_name:
                self.stop_audio()

                # Play the audio on the remote server
                # mp3-player-server expects the full name with extension
                if self.audio_client.play_audio(audio_name, volume=100, loop=True):
                    self.running = True
                    self.current_audio_name = audio_name
                    print(f"Started playing: {audio_name}")
                else:
                    print(f"Failed to start audio playback for {audio_name}")

    def stop_audio(self):
        """Stop current audio playback"""
        if self.running:
            self.audio_client.stop_playback()
            self.running = False
            previous = self.current_audio_name
            self.current_audio_name = None
            if previous:
                print(f"Stopped playing: {previous}")