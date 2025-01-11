import subprocess
import os

from app.jobs.audio_manager import AudioManager


class AudioManagerImpl(AudioManager):
    def __init__(self):
        self.running = False
        self.process = None
        self.audio_path = None


    def start_audio(self, path):
        if self.audio_path is None or not self.audio_path == path:
            self.stop_audio() # Stop the previous audio if it is different and play new audio, if not the old one keeps playing
            self.running = True

            command = "aplay -l | grep 'bcm2835' | awk '{gsub(\":\",\"\",$0); print $2 \",\" $7}'"
            output = os.popen(command).read().strip()

            self.process = subprocess.Popen(["mpg123", "-f", "32768", "-a", f"plughw:{output}", "--loop", "-1", path])
            self.audio_path = path


    def stop_audio(self):
        if self.running:
            self.running = False
            if self.process is not None:
                self.process.terminate()
                self.process = None
        self.audio_path = None
