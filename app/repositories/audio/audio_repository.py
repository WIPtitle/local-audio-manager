from abc import ABC, abstractmethod

from fastapi import UploadFile


class AudioRepository(ABC):
    @abstractmethod
    def get_alarm_audio(self):
        pass

    @abstractmethod
    def get_waiting_audio(self):
        pass

    @abstractmethod
    def create_alarm_audio(self, file: UploadFile):
        pass

    @abstractmethod
    def delete_alarm_audio(self):
        pass
