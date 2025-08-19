from pathlib import Path
from app.jobs.audio_manager import AudioManager
from app.clients.audio_server_client import AudioServerClient


class AudioManagerImpl(AudioManager):
    def __init__(self, audio_client: AudioServerClient):
        self.audio_client = audio_client
        self.running = False
        self.current_audio_name = None

    def start_audio(self, path):
        # Convert path to audio name for the server
        if isinstance(path, (str, Path)):
            path = Path(path)
            audio_name = path.stem  # Get filename without extension

            # Only restart if it's a different audio
            if self.current_audio_name != audio_name:
                self.stop_audio()

                # Play the audio on the remote server
                if self.audio_client.play_audio(audio_name, volume=100, loop=True):
                    self.running = True
                    self.current_audio_name = audio_name
                else:
                    print(f"Failed to start audio playback for {audio_name}")

    def stop_audio(self):
        if self.running:
            self.audio_client.stop_playback()
            self.running = False
            self.current_audio_name = None