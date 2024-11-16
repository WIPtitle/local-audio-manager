import subprocess

from app.jobs.audio_manager import AudioManager


class AudioManagerImpl(AudioManager):
    def __init__(self):
        self.running = False
        self.process = None


    def start_audio(self, path):
        self.stop_audio() # just in case, stop before starting new audio
        self.running = True
        self.process = subprocess.Popen(["mpg123", "--loop", "-1", path])


    def stop_audio(self):
        if self.running:
            self.running = False
            if self.process is not None:
                self.process.terminate()
                self.process = None
