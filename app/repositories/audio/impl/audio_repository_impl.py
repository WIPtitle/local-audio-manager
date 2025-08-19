from pathlib import Path
from fastapi import UploadFile
from app.exceptions.not_found_exception import NotFoundException
from app.repositories.audio.audio_repository import AudioRepository
from app.clients.audio_server_client import AudioServerClient


class AudioRepositoryImpl(AudioRepository):
    def __init__(self, audio_client: AudioServerClient):
        self.path = Path("/var/lib/local-audio-manager/data/")
        self.path.mkdir(parents=True, exist_ok=True)
        self.audio_client = audio_client

        # Check and upload audio files if needed
        self._ensure_waiting_audio()
        self._ensure_alarm_audio()

    def _ensure_waiting_audio(self):
        """Ensure waiting.mp3 exists on the server"""
        waiting_file = self.path / "waiting.mp3"
        if waiting_file.exists():
            # Check if it exists on the server, upload if not
            if not self.audio_client.check_audio_exists("waiting"):
                self.audio_client.upload_audio("waiting", waiting_file)

    def _ensure_alarm_audio(self):
        """Ensure alarm audio exists on the server"""
        files = [f for f in self.path.glob("*") if f.name != "waiting.mp3"]
        if files:
            alarm_file = files[0]
            # Check if it exists on the server, upload if not
            audio_name = alarm_file.name
            if not self.audio_client.check_audio_exists(audio_name):
                self.audio_client.upload_audio(audio_name, alarm_file)

    def get_alarm_audio(self):
        files = [f for f in self.path.glob("*") if f.name != "waiting.mp3"]
        if files:
            return files[0]
        raise NotFoundException("Audio was not found")

    def get_waiting_audio(self):
        file = self.path / "waiting.mp3"
        if file.exists():
            return file
        raise NotFoundException("Audio was not found")

    def create_alarm_audio(self, file: UploadFile):
        # First delete existing alarm audio
        self.delete_alarm_audio()

        filename = file.filename
        if file.filename == "waiting.mp3":
            filename = "alarm.mp3"  # do not override the waiting file ever, use a different name

        # Save file locally
        file_path = self.path / filename
        with file_path.open("wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Upload to audio server
        audio_name = file_path.stem  # Get name without extension
        self.audio_client.upload_audio(audio_name, file_path)

    def delete_alarm_audio(self) -> None:
        for f in self.path.glob("*"):
            if f.name != "waiting.mp3":
                # Delete from server
                audio_name = f.stem
                self.audio_client.delete_audio(audio_name)
                # Delete local file
                f.unlink()