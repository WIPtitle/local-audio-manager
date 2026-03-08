from typing import List, Set

from fastapi import Response
from pydantic import BaseModel

from app.clients.audio_server_client import AudioServerClient, AudioType
from app.config.bindings import inject, bindings
from app.repositories.audio.audio_repository import AudioRepository
from app.routers.router_wrapper import RouterWrapper


class Mp3ServerConfig(BaseModel):
    url: str
    types: List[str]
    volume_alarm: int = 100
    volume_waiting: int = 100
    volume_warning: int = 100


class InternalConfigRouter(RouterWrapper):
    @inject
    def __init__(self, audio_repository: AudioRepository):
        super().__init__(prefix="/internal")
        self.audio_repository = audio_repository

    def _define_routes(self):
        @self.router.post("/reload-mp3-config")
        def reload_mp3_config(servers: List[Mp3ServerConfig]):
            audio_clients: List[AudioServerClient] = bindings['audio_clients']

            # Close existing clients
            for client in audio_clients:
                try:
                    client.close()
                except Exception:
                    pass

            # Build new clients
            new_clients: List[AudioServerClient] = []
            for server in servers:
                types: Set[AudioType] = set()
                for t in server.types:
                    try:
                        types.add(AudioType(t))
                    except ValueError:
                        pass
                if not types:
                    types = {AudioType.ALARM, AudioType.WAITING, AudioType.WARNING}

                volumes = {
                    AudioType.ALARM: server.volume_alarm,
                    AudioType.WAITING: server.volume_waiting,
                    AudioType.WARNING: server.volume_warning,
                }
                client = AudioServerClient(base_url=server.url, audio_types=types, volumes=volumes)
                new_clients.append(client)
                types_str = ",".join(t.value for t in types)
                print(f"Reloaded MP3 player client for {server.url} with types [{types_str}]")

            # Replace in-place so all references update
            audio_clients.clear()
            audio_clients.extend(new_clients)

            print(f"MP3 config reloaded: {len(new_clients)} server(s)")

            # Ensure audio files are synced to new servers
            self.audio_repository.ensure_all_audio_on_servers()

            return Response(status_code=204)
