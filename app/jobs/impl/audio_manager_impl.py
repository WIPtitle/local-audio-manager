from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.jobs.audio_manager import AudioManager
from app.clients.audio_server_client import AudioServerClient


class AudioManagerImpl(AudioManager):
    def __init__(self, audio_clients: List[AudioServerClient]):
        """Initialize with a list of audio server clients

        Args:
            audio_clients: List of AudioServerClient instances
        """
        self.audio_clients = audio_clients
        self.running = False
        self.current_audio_name = None
        print(f"AudioManager initialized with {len(audio_clients)} MP3 player servers")

    def start_audio(self, path):
        """Start playing an audio file on all servers

        Args:
            path: Can be a string path or Path object to the audio file
        """
        # Convert to Path object if string
        if isinstance(path, (str, Path)):
            path = Path(path)
            # Get full filename with extension
            audio_name = path.name

            # Only restart if it's a different audio
            if self.current_audio_name != audio_name:
                self.stop_audio()

                # Play the audio on all servers in parallel
                def play_on_server(client: AudioServerClient) -> tuple[str, bool]:
                    success = client.play_audio(audio_name, volume=100, loop=True)
                    return client.base_url, success

                results = {}
                with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
                    futures = [executor.submit(play_on_server, client) for client in self.audio_clients]

                    for future in as_completed(futures):
                        url, success = future.result()
                        results[url] = success

                # Check if at least one server started playing
                success_count = sum(1 for success in results.values() if success)

                if success_count > 0:
                    self.running = True
                    self.current_audio_name = audio_name
                    print(f"Started playing {audio_name} on {success_count}/{len(results)} servers")

                    # Log failures
                    for url, success in results.items():
                        if not success:
                            print(f"Failed to start {audio_name} on {url}")
                else:
                    print(f"Failed to start audio playback for {audio_name} on all servers")

    def stop_audio(self):
        """Stop current audio playback on all servers"""
        if self.running:
            # Stop on all servers in parallel
            def stop_on_server(client: AudioServerClient) -> tuple[str, bool]:
                success = client.stop_playback()
                return client.base_url, success

            results = {}
            with ThreadPoolExecutor(max_workers=len(self.audio_clients)) as executor:
                futures = [executor.submit(stop_on_server, client) for client in self.audio_clients]

                for future in as_completed(futures):
                    url, success = future.result()
                    results[url] = success

            # Check results
            success_count = sum(1 for success in results.values() if success)

            self.running = False
            previous = self.current_audio_name
            self.current_audio_name = None

            if previous:
                print(f"Stopped playing {previous} on {success_count}/{len(results)} servers")

                # Log failures
                for url, success in results.items():
                    if not success:
                        print(f"Failed to stop playback on {url}")