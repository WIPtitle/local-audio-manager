from abc import ABC, abstractmethod

from fastapi import UploadFile


class AudioRepository(ABC):
    @abstractmethod
    def get_audio(self):
        pass

    @abstractmethod
    def create_audio(self, file: UploadFile):
        pass
