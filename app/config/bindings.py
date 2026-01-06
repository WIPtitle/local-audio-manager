import os
from functools import wraps
from typing import Callable, get_type_hints, List

from app.clients.auth_client import AuthClient
from app.jobs.audio_manager import AudioManager
from app.jobs.impl.audio_manager_impl import AudioManagerImpl
from app.repositories.audio.impl.audio_repository_impl import AudioRepositoryImpl
from app.services.audio.audio_service import AudioService
from app.services.audio.impl.audio_service_impl import AudioServiceImpl
from app.clients.audio_server_client import AudioServerClient, AudioType

bindings = {}

mp3_urls = os.getenv('MP3_PLAYER_SERVER_URLS', 'http://localhost:8888')
mp3_server_urls = [url.strip() for url in mp3_urls.split(',')]
audio_clients: List[AudioServerClient] = []

for mp3_url in mp3_server_urls:
    audio_type = AudioType.BOTH
    url = mp3_url

    if '@' in mp3_url:
        parts = mp3_url.split('@', 1)
        if len(parts) == 2:
            type_str, url = parts
            type_str = type_str.upper()
            if type_str in [t.value for t in AudioType]:
                audio_type = AudioType(type_str)

    client = AudioServerClient(base_url=url, audio_type=audio_type)
    audio_clients.append(client)
    print(f"Created MP3 player client for {url} with type {audio_type.value}")

audio_repository = AudioRepositoryImpl(audio_clients)
audio_manager = AudioManagerImpl(audio_clients)

audio_service = AudioServiceImpl(audio_repository, audio_manager)

bindings[AudioService] = audio_service
bindings[AudioManager] = audio_manager
bindings['audio_clients'] = audio_clients

bindings[AuthClient] = AuthClient()


def resolve(interface):
    implementation = bindings[interface]
    if implementation is None:
        raise ValueError(f"No binding found for {interface}")
    return implementation


def inject(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        type_hints = get_type_hints(func)
        for name, param_type in type_hints.items():
            if param_type in bindings:
                kwargs[name] = resolve(param_type)
        return func(*args, **kwargs)
    return wrapper