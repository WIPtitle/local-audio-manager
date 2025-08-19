import os
from pathlib import Path

import httpx


class AudioServerClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('MP3_PLAYER_SERVER_URL', 'http://localhost:8888')
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def check_audio_exists(self, name: str) -> bool:
        """Check if an audio file exists on the server

        Args:
            name: Audio name with .mp3 extension
        """
        try:
            response = self.client.get(f"/api/audio/{name}")
            return response.status_code == 200
        except:
            return False

    def upload_audio(self, name: str, file_path: Path) -> bool:
        """Upload an audio file to the server

        Args:
            name: Audio name with .mp3 extension
            file_path: Path to the mp3 file to upload
        """
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
        """Delete an audio file from the server

        Args:
            name: Audio name with .mp3 extension
        """
        try:
            response = self.client.delete(f"/api/audio/{name}")
            return response.status_code in [200, 404]  # OK even if not found
        except:
            return False

    def play_audio(self, name: str, volume: int = 100, loop: bool = True) -> bool:
        """Start playing an audio file

        Args:
            name: Audio name with .mp3 extension
            volume: Volume level 0-100
            loop: Whether to loop the audio
        """
        try:
            response = self.client.post(
                f"/api/play/{name}",
                params={"volume": volume, "loop": loop}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to play audio {name}: {e}")
            return False

    def stop_playback(self) -> bool:
        """Stop current audio playback"""
        try:
            response = self.client.post("/api/stop")
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to stop playback: {e}")
            return False

    def list_audio_files(self) -> list:
        """List all audio files on the server"""
        try:
            response = self.client.get("/api/audio")
            if response.status_code == 200:
                return response.json().get('files', [])
        except:
            pass
        return []

    def close(self):
        """Close the HTTP client"""
        self.client.close()