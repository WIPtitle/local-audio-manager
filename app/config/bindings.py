import os
from functools import wraps
from typing import Callable, get_type_hints

from rabbitmq_sdk.client.impl.rabbitmq_client_impl import RabbitMQClientImpl
from rabbitmq_sdk.enums.service import Service

from app.consumers.alarm_stopped_consumer import AlarmStoppedConsumer
from app.consumers.camera_alarm_consumer import CameraAlarmConsumer
from app.consumers.reed_alarm_consumer import ReedAlarmConsumer
from app.jobs.audio_manager import AudioManager
from app.jobs.impl.audio_manager_impl import AudioManagerImpl
from app.repositories.audio.impl.audio_repository_impl import AudioRepositoryImpl
from app.services.audio.audio_service import AudioService
from app.services.audio.impl.audio_service_impl import AudioServiceImpl
from app.utils.read_credentials import read_credentials

bindings = { }

rabbit_credentials = read_credentials(os.getenv('RBBT_CREDENTIALS_FILE'))
rabbitmq_client = RabbitMQClientImpl.from_config(
    host=os.getenv("RABBITMQ_HOSTNAME"), # using container name as host instead of ip
    port=5672,
    username=rabbit_credentials['RABBITMQ_USER'],
    password=rabbit_credentials['RABBITMQ_PASSWORD']
).with_current_service(Service.AUDIO_MANAGER)

# Create instances only one time
audio_repository = AudioRepositoryImpl()
audio_manager = AudioManagerImpl()

audio_service = AudioServiceImpl(audio_repository, audio_manager)

# Consumers
alarm_stopped_consumer = AlarmStoppedConsumer(audio_service)
camera_alarm_consumer = CameraAlarmConsumer(audio_service)
reed_alarm_consumer = ReedAlarmConsumer(audio_service)

rabbitmq_client.consume(alarm_stopped_consumer)
rabbitmq_client.consume(camera_alarm_consumer)
rabbitmq_client.consume(reed_alarm_consumer)

# Put them in an interface -> instance dict so they will be used everytime a dependency is required
bindings[AudioService] = audio_service
bindings[AudioManager] = audio_manager


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