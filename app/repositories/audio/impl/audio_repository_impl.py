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
            # Check if it exists on the server
            if not self.audio_client.check_audio_exists("waiting.mp3"):
                # Upload with full filename
                self.audio_client.upload_audio("waiting.mp3", waiting_file)

    def _ensure_alarm_audio(self):
        """Ensure alarm audio exists on the server"""
        files = [f for f in self.path.glob("*.mp3") if f.name != "waiting.mp3"]
        if files:
            alarm_file = files[0]
            # Use full filename with extension
            audio_name = alarm_file.name
            # Check if it exists on the server
            if not self.audio_client.check_audio_exists(audio_name):
                # Upload with full filename
                self.audio_client.upload_audio(audio_name, alarm_file)

    def get_alarm_audio(self):
        """Get the alarm audio file path"""
        files = [f for f in self.path.glob("*.mp3") if f.name != "waiting.mp3"]
        if files:
            return files[0]
        raise NotFoundException("Audio was not found")

    def get_waiting_audio(self):
        """Get the waiting audio file path"""
        file = self.path / "waiting.mp3"
        if file.exists():
            return file
        raise NotFoundException("Audio was not found")

    def create_alarm_audio(self, file: UploadFile):
        """Create/update the alarm audio file"""
        # First delete existing alarm audio (both locally and on server)
        self.delete_alarm_audio()

        # Sanitize filename - remove special characters but keep it recognizable
        original_name = file.filename
        if original_name == "waiting.mp3":
            # Never override the waiting file
            filename = "alarm.mp3"
        else:
            # Ensure it ends with .mp3
            if not original_name.lower().endswith('.mp3'):
                filename = original_name + '.mp3'
            else:
                filename = original_name

        # Save file locally
        file_path = self.path / filename
        with file_path.open("wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Upload to audio server with full filename
        self.audio_client.upload_audio(filename, file_path)

    def delete_alarm_audio(self) -> None:
        """Delete all alarm audio files (not waiting.mp3)"""
        for f in self.path.glob("*.mp3"):
            if f.name != "waiting.mp3":
                # Delete from server using full filename
                self.audio_client.delete_audio(f.name)
                # Delete local file
                f.unlink()