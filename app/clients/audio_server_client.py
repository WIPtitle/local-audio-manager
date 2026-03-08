from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set

import httpx


class AudioType(Enum):
    ALARM = "ALARM"
    WAITING = "WAITING"
    WARNING = "WARNING"


class AudioServerClient:
    def __init__(self, base_url: str, audio_types: Set[AudioType], volumes: Optional[Dict[AudioType, int]] = None):
        self.base_url = base_url
        self.audio_types = audio_types
        self.volumes = volumes or {t: 100 for t in AudioType}
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def get_volume(self, audio_type: AudioType) -> int:
        return self.volumes.get(audio_type, 100)

    def check_audio_exists(self, name: str) -> bool:
        try:
            response = self.client.get(f"/api/audio/{name}")
            return response.status_code == 200
        except:
            return False

    def upload_audio(self, name: str, file_path: Path) -> bool:
        try:
            with open(file_path, 'rb') as f:
                response = self.client.put(
                    f"/api/audio/{name}",
                    content=f.read(),
                    headers={"Content-Type": "audio/mpeg"}
                )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to upload audio {name}: {e}")
            return False

    def delete_audio(self, name: str) -> bool:
        try:
            response = self.client.delete(f"/api/audio/{name}")
            return response.status_code in [200, 404]
        except:
            return False

    def play_audio(self, name: str, volume: int = 100, loop: bool = True, duration: int = None) -> bool:
        try:
            response = self.client.post(
                f"/api/play/{name}",
                params={"volume": volume, "loop": loop, "duration": duration}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to play audio {name}: {e}")
            return False

    def stop_playback(self) -> bool:
        try:
            response = self.client.post("/api/stop")
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to stop playback: {e}")
            return False

    def list_audio_files(self) -> list:
        try:
            response = self.client.get("/api/audio")
            if response.status_code == 200:
                return response.json().get('files', [])
        except:
            pass
        return []

    def close(self):
        self.client.close()
