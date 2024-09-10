from abc import abstractmethod


class AudioThread:
    @abstractmethod
    def start_audio(self, path: str):
        pass

    @abstractmethod
    def stop_audio(self):
        pass