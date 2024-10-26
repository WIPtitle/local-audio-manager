from abc import abstractmethod


class AudioManager:
    @abstractmethod
    def start_audio(self, path: str):
        pass

    @abstractmethod
    def stop_audio(self):
        pass