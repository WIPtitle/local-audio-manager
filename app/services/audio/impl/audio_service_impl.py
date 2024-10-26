from fastapi import UploadFile

from app.jobs.audio_thread import AudioThread
from app.repositories.audio.audio_repository import AudioRepository
from app.services.audio.audio_service import AudioService


class AudioServiceImpl(AudioService):
    def __init__(self, audio_repository: AudioRepository, audio_thread: AudioThread):
        self.audio_repository = audio_repository
        self.audio_thread = audio_thread


    def get_audio(self):
        return self.audio_repository.get_audio()


    def create_audio(self, file: UploadFile):
        self.audio_repository.create_audio(file)


    def start_audio(self):
        file = self.audio_repository.get_audio()
        self.audio_thread.start_audio(file)


    def stop_audio(self):
        self.audio_thread.stop_audio()


    def delete_audio(self):
        self.audio_repository.delete_audio()