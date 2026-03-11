from fastapi import UploadFile

from app.exceptions.not_found_exception import NotFoundException
from app.jobs.audio_manager import AudioManager
from app.repositories.audio.audio_repository import AudioRepository
from app.services.audio.audio_service import AudioService


class AudioServiceImpl(AudioService):
    def __init__(self, audio_repository: AudioRepository, audio_manager: AudioManager):
        self.audio_repository = audio_repository
        self.audio_manager = audio_manager

    def get_audio(self):
        return self.audio_repository.get_alarm_audio()

    def create_audio(self, file: UploadFile):
        self.audio_repository.create_alarm_audio(file)

    def start_audio(self, duration: int = None):
        file = self.audio_repository.get_alarm_audio()
        self.audio_manager.start_audio(file, duration=duration)

    def stop_audio(self):
        self.audio_manager.stop_audio()

    def start_waiting_audio(self, duration: int = None):
        try:
            file = self.audio_repository.get_waiting_audio()
            self.audio_manager.start_audio(file, duration=duration)
        except NotFoundException:
            pass

    def start_warning_audio(self):
        try:
            file = self.audio_repository.get_warning_audio()
            self.audio_manager.start_warning_audio(file)
        except NotFoundException:
            pass

    def get_warning_audio(self):
        return self.audio_repository.get_warning_audio()

    def create_warning_audio(self, file: UploadFile):
        self.audio_repository.create_warning_audio(file)

    def delete_warning_audio(self):
        self.audio_repository.delete_warning_audio()

    def delete_audio(self):
        self.audio_repository.delete_alarm_audio()
