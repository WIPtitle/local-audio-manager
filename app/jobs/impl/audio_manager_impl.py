from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.jobs.audio_manager import AudioManager
from app.clients.audio_server_client import AudioServerClient, AudioType


class AudioManagerImpl(AudioManager):
    def __init__(self, audio_clients: List[AudioServerClient]):
        self.audio_clients = audio_clients
        self.current_audio_type: Optional[AudioType] = None
        self.current_audio_name: Optional[str] = None
        print(f"AudioManager initialized with {len(audio_clients)} MP3 player servers")

    def _get_clients_for_type(self, audio_type: AudioType) -> List[AudioServerClient]:
        return [c for c in self.audio_clients if audio_type in c.audio_types]

    def _stop_all_clients(self):
        if not self.audio_clients:
            self.current_audio_type = None
            self.current_audio_name = None
            return

        def stop_on_server(client: AudioServerClient) -> tuple[str, bool]:
            success = client.stop_playback()
            return client.base_url, success

        with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
            futures = [executor.submit(stop_on_server, c) for c in self.audio_clients]
            for future in as_completed(futures):
                url, success = future.result()
                if not success:
                    print(f"Failed to stop playback on {url}")

        previous = self.current_audio_name
        self.current_audio_type = None
        self.current_audio_name = None

        if previous:
            print(f"Stopped playing {previous}")

    def _play(self, audio_name: str, audio_type: AudioType, loop: bool, duration: int | None):
        if loop and not duration:
            raise ValueError(f"duration is required when loop=True (audio: {audio_name})")

        self._stop_all_clients()

        relevant_clients = self._get_clients_for_type(audio_type)

        if not relevant_clients:
            print(f"No servers configured for {audio_type.value} audio")
            return

        def play_on_server(client: AudioServerClient) -> tuple[str, bool]:
            volume = client.get_volume(audio_type)
            success = client.play_audio(audio_name, volume=volume, loop=loop, duration=duration)
            return client.base_url, success

        results = {}
        with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
            futures = [executor.submit(play_on_server, client) for client in relevant_clients]
            for future in as_completed(futures):
                url, success = future.result()
                results[url] = success

        success_count = sum(1 for success in results.values() if success)

        if success_count > 0:
            self.current_audio_type = audio_type
            self.current_audio_name = audio_name
            print(f"Started playing {audio_name} ({audio_type.value}) on {success_count}/{len(results)} servers")

            for url, success in results.items():
                if not success:
                    print(f"Failed to start {audio_name} on {url}")
        else:
            print(f"Failed to start audio playback for {audio_name} on all servers")

    MAX_AUDIO_DURATION = 300

    def start_audio(self, path, duration: int = None):
        if isinstance(path, (str, Path)):
            path = Path(path)
            audio_name = path.name
            is_waiting = audio_name == "waiting.mp3"
            audio_type = AudioType.WAITING if is_waiting else AudioType.ALARM
            capped_duration = min(duration, self.MAX_AUDIO_DURATION) if duration is not None else None
            self._play(audio_name, audio_type, loop=True, duration=capped_duration)

    def start_warning_audio(self, path):
        if self.current_audio_type == AudioType.ALARM:
            return

        if isinstance(path, (str, Path)):
            path = Path(path)
            self._play(path.name, AudioType.WARNING, loop=False, duration=None)

    def stop_audio(self):
        self._stop_all_clients()
