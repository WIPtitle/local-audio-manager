from typing import Type

from rabbitmq_sdk.consumer.base_consumer import BaseConsumer
from rabbitmq_sdk.enums.event import Event
from rabbitmq_sdk.event.base_event import BaseEvent
from rabbitmq_sdk.event.impl.devices_manager.alarm_stopped import AlarmStopped

from app.services.audio.audio_service import AudioService


class AlarmStoppedConsumer(BaseConsumer):
    def __init__(self, audio_service: AudioService):
        super().__init__()
        self.audio_service = audio_service

    def get_event(self) -> Event:
        return Event.ALARM_STOPPED

    def event_class(self) -> Type[BaseEvent]:
        return AlarmStopped

    def do_handle(self, event):
        event: AlarmStopped = AlarmStopped.from_dict(event)
        print("STOPPING AUDIO")
        try:
            self.audio_service.stop_audio()
        except:
            pass