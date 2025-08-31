from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import UploadFile
from app.exceptions.not_found_exception import NotFoundException
from app.repositories.audio.audio_repository import AudioRepository
from app.clients.audio_server_client import AudioServerClient


class AudioRepositoryImpl(AudioRepository):
    def __init__(self, audio_clients: List[AudioServerClient]):
        """Initialize with a list of audio server clients

        Args:
            audio_clients: List of AudioServerClient instances
        """
        self.path = Path("/var/lib/local-audio-manager/data/")
        self.path.mkdir(parents=True, exist_ok=True)
        self.audio_clients = audio_clients

        # Check and upload audio files to all servers if needed
        self._ensure_waiting_audio()
        self._ensure_alarm_audio()

    def _ensure_waiting_audio(self):
        """Ensure waiting.mp3 exists on all servers"""
        waiting_file = self.path / "waiting.mp3"
        if waiting_file.exists():
            # Upload to all servers in parallel
            def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
                # Check if it already exists
                if not client.check_audio_exists("waiting.mp3"):
                    success = client.upload_audio("waiting.mp3", waiting_file)
                    return client.base_url, success
                return client.base_url, True  # Already exists

            with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
                futures = [executor.submit(upload_to_server, client) for client in self.audio_clients]

                for future in as_completed(futures):
                    url, success = future.result()
                    if success:
                        print(f"Ensured waiting.mp3 on {url}")
                    else:
                        print(f"Failed to ensure waiting.mp3 on {url}")

    def _ensure_alarm_audio(self):
        """Ensure alarm audio exists on all servers"""
        files = [f for f in self.path.glob("*.mp3") if f.name != "waiting.mp3"]
        if files:
            alarm_file = files[0]
            audio_name = alarm_file.name

            # Upload to all servers in parallel
            def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
                # Check if it already exists
                if not client.check_audio_exists(audio_name):
                    success = client.upload_audio(audio_name, alarm_file)
                    return client.base_url, success
                return client.base_url, True  # Already exists

            with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
                futures = [executor.submit(upload_to_server, client) for client in self.audio_clients]

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
        """Create/update the alarm audio file on all servers"""
        # First delete existing alarm audio from all servers
        self.delete_alarm_audio()

        # Sanitize filename - remove special characters but keep it recognizable
        original_name = file.filename
        if original_name == "waiting.mp3":
            # Never override the waiting file
            filename = "alarm.mp3"
        else:
            # Ensure it ends with .mp3
            if not original_name.lower().endswith('.mp3'):
                filename = original_name + '.mp3'
            else:
                filename = original_name

        # Save file locally
        file_path = self.path / filename
        with file_path.open("wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Upload to all audio servers in parallel
        def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
            success = client.upload_audio(filename, file_path)
            return client.base_url, success

        with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
            futures = [executor.submit(upload_to_server, client) for client in self.audio_clients]

            for future in as_completed(futures):
                url, success = future.result()
                if success:
                    print(f"Uploaded {filename} to {url}")
                else:
                    print(f"Failed to upload {filename} to {url}")

    def delete_alarm_audio(self) -> None:
        """Delete all alarm audio files from all servers"""
        for f in self.path.glob("*.mp3"):
            if f.name != "waiting.mp3":
                # Delete from all servers in parallel
                def delete_from_server(client: AudioServerClient) -> tuple[str, bool]:
                    success = client.delete_audio(f.name)
                    return client.base_url, success

                with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
                    futures = [executor.submit(delete_from_server, client) for client in self.audio_clients]

                    for future in as_completed(futures):
                        url, success = future.result()
                        if success:
                            print(f"Deleted {f.name} from {url}")
                        else:
                            print(f"Failed to delete {f.name} from {url}")

                # Delete local file
                f.unlink()