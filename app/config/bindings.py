from functools import wraps
from typing import Callable, get_type_hints, List

from app.clients.auth_client import AuthClient
from app.jobs.audio_manager import AudioManager
from app.jobs.impl.audio_manager_impl import AudioManagerImpl
from app.repositories.audio.audio_repository import AudioRepository
from app.repositories.audio.impl.audio_repository_impl import AudioRepositoryImpl
from app.services.audio.audio_service import AudioService
from app.services.audio.impl.audio_service_impl import AudioServiceImpl
from app.clients.audio_server_client import AudioServerClient

bindings = {}

# Start with empty clients - devices-manager will push config via /internal/reload-mp3-config
audio_clients: List[AudioServerClient] = []

audio_repository = AudioRepositoryImpl(audio_clients)
audio_manager = AudioManagerImpl(audio_clients)

audio_service = AudioServiceImpl(audio_repository, audio_manager)

bindings[AudioService] = audio_service
bindings[AudioManager] = audio_manager
bindings[AudioRepository] = audio_repository
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
