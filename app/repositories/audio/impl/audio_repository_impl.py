from pathlib import Path

from fastapi import UploadFile

from app.exceptions.not_found_exception import NotFoundException
from app.repositories.audio.audio_repository import AudioRepository


class AudioRepositoryImpl(AudioRepository):
    def __init__(self):
        self.path = Path("/var/lib/local-audio-manager/data/")
        self.path.mkdir(parents=True, exist_ok=True)


    def get_audio(self):
        files = [f for f in self.path.glob("*") if f.name != "waiting.mp3"]
        if files:
            return files[0]
        raise NotFoundException("Audio was not found")


    def get_waiting_audio(self):
        file = self.path / "waiting.mp3"
        if file.exists():
            return file
        raise NotFoundException("Audio was not found")


    def create_audio(self, file: UploadFile):
        for f in self.path.glob("*"):
            f.unlink()

        file_path = self.path / file.filename
        with file_path.open("wb") as buffer:
            buffer.write(file.file.read())


    def delete_audio(self) -> None:
        for f in self.path.glob("*"):
            f.unlink()
