from abc import ABC, abstractmethod

from fastapi import UploadFile


class AudioService(ABC):
    @abstractmethod
    def get_audio(self):
        pass

    @abstractmethod
    def create_audio(self, file: UploadFile):
        pass

    @abstractmethod
    def start_audio(self, duration: int = None):
        pass

    @abstractmethod
    def stop_audio(self):
        pass

    @abstractmethod
    def start_waiting_audio(self, duration: int = None):
        pass

    @abstractmethod
    def start_warning_audio(self):
        pass

    @abstractmethod
    def get_warning_audio(self):
        pass

    @abstractmethod
    def create_warning_audio(self, file: UploadFile):
        pass

    @abstractmethod
    def delete_warning_audio(self):
        pass

    @abstractmethod
    def delete_audio(self):
        pass
