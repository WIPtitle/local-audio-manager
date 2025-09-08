from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import UploadFile
from app.exceptions.not_found_exception import NotFoundException
from app.repositories.audio.audio_repository import AudioRepository
from app.clients.audio_server_client import AudioServerClient, AudioType


class AudioRepositoryImpl(AudioRepository):
    def __init__(self, audio_clients: List[AudioServerClient]):
        """Initialize with a list of audio server clients

        Args:
            audio_clients: List of AudioServerClient instances
        """
        self.path = Path("/var/lib/local-audio-manager/data/")
        self.path.mkdir(parents=True, exist_ok=True)
        self.audio_clients = audio_clients

        self._ensure_waiting_audio()
        self._ensure_alarm_audio()

    def _ensure_waiting_audio(self):
        """Ensure waiting.mp3 exists on appropriate servers"""
        waiting_file = self.path / "waiting.mp3"
        if waiting_file.exists():
            relevant_clients = [
                client for client in self.audio_clients
                if client.audio_type in [AudioType.WAITING, AudioType.BOTH]
            ]

            if not relevant_clients:
                return

            def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
                if not client.check_audio_exists("waiting.mp3"):
                    success = client.upload_audio("waiting.mp3", waiting_file)
                    return client.base_url, success
                return client.base_url, True

            with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
                futures = [executor.submit(upload_to_server, client) for client in relevant_clients]

                for future in as_completed(futures):
                    url, success = future.result()
                    if success:
                        print(f"Ensured waiting.mp3 on {url}")
                    else:
                        print(f"Failed to ensure waiting.mp3 on {url}")

    def _ensure_alarm_audio(self):
        """Ensure alarm audio exists on appropriate servers"""
        files = [f for f in self.path.glob("*.mp3") if f.name != "waiting.mp3"]
        if files:
            alarm_file = files[0]
            audio_name = alarm_file.name

            relevant_clients = [
                client for client in self.audio_clients
                if client.audio_type in [AudioType.ALARM, AudioType.BOTH]
            ]

            if not relevant_clients:
                return

            def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
                if not client.check_audio_exists(audio_name):
                    success = client.upload_audio(audio_name, alarm_file)
                    return client.base_url, success
                return client.base_url, True

            with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
                futures = [executor.submit(upload_to_server, client) for client in relevant_clients]

                for future in as_completed(futures):
                    url, success = future.result()
                    if success:
                        print(f"Ensured {audio_name} on {url}")
                    else:
                        print(f"Failed to ensure {audio_name} on {url}")

    def get_alarm_audio(self):
        """Get the alarm audio file path"""
        files = [f for f in self.path.glob("*.mp3") if f.name != "waiting.mp3"]
        if files:
            return files[0]
        raise NotFoundException("Audio was not found")

    def get_waiting_audio(self):
        """Get the waiting audio file path"""
        file = self.path / "waiting.mp3"
        if file.exists():
            return file
        raise NotFoundException("Audio was not found")

    def create_alarm_audio(self, file: UploadFile):
        """Create/update the alarm audio file on appropriate servers"""
        self.delete_alarm_audio()

        original_name = file.filename
        if original_name == "waiting.mp3":
            filename = "alarm.mp3"
        else:
            if not original_name.lower().endswith('.mp3'):
                filename = original_name + '.mp3'
            else:
                filename = original_name

        file_path = self.path / filename
        with file_path.open("wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        relevant_clients = [
            client for client in self.audio_clients
            if client.audio_type in [AudioType.ALARM, AudioType.BOTH]
        ]

        if not relevant_clients:
            print(f"No servers configured to receive alarm audio")
            return

        def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
            success = client.upload_audio(filename, file_path)
            return client.base_url, success

        with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
            futures = [executor.submit(upload_to_server, client) for client in relevant_clients]

            for future in as_completed(futures):
                url, success = future.result()
                if success:
                    print(f"Uploaded {filename} to {url}")
                else:
                    print(f"Failed to upload {filename} to {url}")

    def delete_alarm_audio(self) -> None:
        """Delete all alarm audio files from appropriate servers"""
        for f in self.path.glob("*.mp3"):
            if f.name != "waiting.mp3":
                relevant_clients = [
                    client for client in self.audio_clients
                    if client.audio_type in [AudioType.ALARM, AudioType.BOTH]
                ]

                if relevant_clients:
                    def delete_from_server(client: AudioServerClient) -> tuple[str, bool]:
                        success = client.delete_audio(f.name)
                        return client.base_url, success

                    with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
                        futures = [executor.submit(delete_from_server, client) for client in relevant_clients]

                        for future in as_completed(futures):
                            url, success = future.result()
                            if success:
                                print(f"Deleted {f.name} from {url}")
                            else:
                                print(f"Failed to delete {f.name} from {url}")

                f.unlink()