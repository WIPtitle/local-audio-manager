from functools import wraps
from typing import Callable, get_type_hints

from app.jobs.audio_thread import AudioThread
from app.jobs.impl.audio_thread_impl import AudioThreadImpl
from app.repositories.audio.impl.audio_repository_impl import AudioRepositoryImpl
from app.services.audio.audio_service import AudioService
from app.services.audio.impl.audio_service_impl import AudioServiceImpl

bindings = { }

# Create instances only one time
audio_repository = AudioRepositoryImpl()
audio_thread = AudioThreadImpl()

audio_service = AudioServiceImpl(audio_repository, audio_thread)

# Put them in an interface -> instance dict so they will be used everytime a dependency is required
bindings[AudioService] = audio_service
bindings[AudioThread] = audio_thread


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