import subprocess

from app.jobs.audio_manager import AudioManager


class AudioManagerImpl(AudioManager):
    def __init__(self):
        self.running = False
        self.process = None
        self.audio_path = None


    def start_audio(self, path):
        if not self.audio_path == path:
            self.stop_audio() # Stop the previous audio if it is different and play new audio, if not the old one keeps playing
            self.running = True
            self.process = subprocess.Popen(["mpg123", "--loop", "-1", path])
            self.audio_path = path


    def stop_audio(self):
        if self.running:
            self.running = False
            if self.process is not None:
                self.process.terminate()
                self.process = None
        self.audio_path = None
