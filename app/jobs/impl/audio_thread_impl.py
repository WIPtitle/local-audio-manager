import threading
import pygame

from app.jobs.audio_thread import AudioThread


class AudioThreadImpl(AudioThread):
    def __init__(self):
        self.running = False
        self.thread = threading.Thread(target=self.entrypoint)


    def entrypoint(self):
        while self.running:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            pygame.time.Clock().tick(10)


    def start_audio(self, path):
        if not self.running:
            self.running = True
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            if not self.thread.is_alive():
                self.thread = threading.Thread(target=self.entrypoint)
                self.thread.start()


    def stop_audio(self):
        if self.running:
            self.running = False
            pygame.mixer.music.stop()