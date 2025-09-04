import os
import time
from functools import wraps
from typing import Callable, get_type_hints, List

from rabbitmq_sdk.client.impl.rabbitmq_client_impl import RabbitMQClientImpl
from rabbitmq_sdk.enums.service import Service

from app.clients.auth_client import AuthClient
from app.consumers.alarm_stopped_consumer import AlarmStoppedConsumer
from app.consumers.alarm_waiting_consumer import AlarmWaitingConsumer
from app.consumers.sensor_alarm_consumer import SensorAlarmConsumer
from app.jobs.audio_manager import AudioManager
from app.jobs.impl.audio_manager_impl import AudioManagerImpl
from app.repositories.audio.impl.audio_repository_impl import AudioRepositoryImpl
from app.services.audio.audio_service import AudioService
from app.services.audio.impl.audio_service_impl import AudioServiceImpl
from app.utils.read_credentials import read_credentials
from app.clients.audio_server_client import AudioServerClient

bindings = { }

rabbit_credentials = read_credentials(os.getenv('RBBT_CREDENTIALS_FILE'))
rabbitmq_client = RabbitMQClientImpl.from_config(
    host=os.getenv("RABBITMQ_HOSTNAME"), # using container name as host instead of ip
    port=5672,
    username=rabbit_credentials['RABBITMQ_USER'],
    password=rabbit_credentials['RABBITMQ_PASSWORD']
).with_current_service(Service.AUDIO_MANAGER)

# Create multiple MP3 Player clients - one for each server
mp3_urls = os.getenv('MP3_PLAYER_SERVER_URLS', 'http://localhost:8888')
mp3_server_urls = [url.strip() for url in mp3_urls.split(',')]
audio_clients: List[AudioServerClient] = []

for mp3_url in mp3_server_urls:
    client = AudioServerClient(base_url=mp3_url)
    audio_clients.append(client)
    print(f"Created MP3 player client for {mp3_url}")

# Create instances only one time
audio_repository = AudioRepositoryImpl(audio_clients)
audio_manager = AudioManagerImpl(audio_clients)

audio_service = AudioServiceImpl(audio_repository, audio_manager)

# Consumers
alarm_stopped_consumer = AlarmStoppedConsumer(audio_service)
sensor_alarm_consumer = SensorAlarmConsumer(audio_service)
alarm_waiting_consumer = AlarmWaitingConsumer(audio_service)

while not rabbitmq_client.consume(alarm_stopped_consumer):
    time.sleep(5)

while not rabbitmq_client.consume(sensor_alarm_consumer):
    time.sleep(5)

while not rabbitmq_client.consume(alarm_waiting_consumer):
    time.sleep(5)

# Put them in an interface -> instance dict so they will be used everytime a dependency is required
bindings[AudioService] = audio_service
bindings[AudioManager] = audio_manager
# Store the list of audio clients
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