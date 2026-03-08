from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import UploadFile
from app.exceptions.not_found_exception import NotFoundException
from app.repositories.audio.audio_repository import AudioRepository
from app.clients.audio_server_client import AudioServerClient, AudioType

RESERVED_FILENAMES = ("waiting.mp3",)


class AudioRepositoryImpl(AudioRepository):
    def __init__(self, audio_clients: List[AudioServerClient]):
        self.path = Path("/var/lib/local-audio-manager/data/")
        self.path.mkdir(parents=True, exist_ok=True)
        self.warning_path = self.path / "warning"
        self.warning_path.mkdir(parents=True, exist_ok=True)
        self.audio_clients = audio_clients

        self._ensure_audio_on_servers("waiting.mp3", AudioType.WAITING)
        self._ensure_warning_audio_on_servers()
        self._ensure_alarm_audio()

    def _get_clients_for_type(self, audio_type: AudioType) -> List[AudioServerClient]:
        return [c for c in self.audio_clients if audio_type in c.audio_types]

    def _ensure_audio_on_servers(self, filename: str, audio_type: AudioType, source_path: Path = None):
        audio_file = source_path or (self.path / filename)
        if not audio_file.exists():
            return

        relevant_clients = self._get_clients_for_type(audio_type)
        if not relevant_clients:
            return

        def upload_to_server(client: AudioServerClient) -> tuple[str, bool]:
            if not client.check_audio_exists(filename):
                success = client.upload_audio(filename, audio_file)
                return client.base_url, success
            return client.base_url, True

        with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
            futures = [executor.submit(upload_to_server, client) for client in relevant_clients]
            for future in as_completed(futures):
                url, success = future.result()
                if success:
                    print(f"Ensured {filename} on {url}")
                else:
                    print(f"Failed to ensure {filename} on {url}")

    def _ensure_warning_audio_on_servers(self):
        files = list(self.warning_path.glob("*.mp3"))
        if not files:
            return
        warning_file = files[0]
        self._ensure_audio_on_servers(warning_file.name, AudioType.WARNING, source_path=warning_file)

    def _ensure_alarm_audio(self):
        files = [f for f in self.path.glob("*.mp3") if f.name not in RESERVED_FILENAMES]
        if not files:
            return

        alarm_file = files[0]
        audio_name = alarm_file.name

        relevant_clients = self._get_clients_for_type(AudioType.ALARM)
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

    # --- Alarm audio ---

    def get_alarm_audio(self):
        files = [f for f in self.path.glob("*.mp3") if f.name not in RESERVED_FILENAMES]
        if files:
            return files[0]
        raise NotFoundException("Alarm audio was not found")

    def create_alarm_audio(self, file: UploadFile):
        self.delete_alarm_audio()

        original_name = file.filename
        if original_name in RESERVED_FILENAMES:
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

        self._upload_to_servers(filename, file_path, AudioType.ALARM)

    def delete_alarm_audio(self) -> None:
        for f in self.path.glob("*.mp3"):
            if f.name not in RESERVED_FILENAMES:
                self._delete_from_servers(f.name, AudioType.ALARM)
                f.unlink()

    # --- Warning audio ---

    def get_warning_audio(self):
        files = list(self.warning_path.glob("*.mp3"))
        if files:
            return files[0]
        raise NotFoundException("Warning audio was not found")

    def create_warning_audio(self, file: UploadFile):
        self.delete_warning_audio()

        original_name = file.filename
        if not original_name.lower().endswith('.mp3'):
            original_name = original_name + '.mp3'

        file_path = self.warning_path / original_name
        with file_path.open("wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        self._upload_to_servers(original_name, file_path, AudioType.WARNING)

    def delete_warning_audio(self) -> None:
        for f in self.warning_path.glob("*.mp3"):
            self._delete_from_servers(f.name, AudioType.WARNING)
            f.unlink()

    # --- Waiting audio ---

    def get_waiting_audio(self):
        file = self.path / "waiting.mp3"
        if file.exists():
            return file
        raise NotFoundException("Waiting audio was not found")

    # --- Helpers ---

    def ensure_all_audio_on_servers(self):
        self._ensure_audio_on_servers("waiting.mp3", AudioType.WAITING)
        self._ensure_warning_audio_on_servers()
        self._ensure_alarm_audio()

    def _upload_to_servers(self, filename: str, file_path: Path, audio_type: AudioType):
        relevant_clients = self._get_clients_for_type(audio_type)
        if not relevant_clients:
            print(f"No servers configured to receive {audio_type.value} audio")
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

    def _delete_from_servers(self, filename: str, audio_type: AudioType):
        relevant_clients = self._get_clients_for_type(audio_type)
        if not relevant_clients:
            return

        def delete_from_server(client: AudioServerClient) -> tuple[str, bool]:
            success = client.delete_audio(filename)
            return client.base_url, success

        with ThreadPoolExecutor(max_workers=len(relevant_clients)) as executor:
            futures = [executor.submit(delete_from_server, client) for client in relevant_clients]
            for future in as_completed(futures):
                url, success = future.result()
                if success:
                    print(f"Deleted {filename} from {url}")
                else:
                    print(f"Failed to delete {filename} from {url}")
