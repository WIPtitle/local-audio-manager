from typing import Type

from rabbitmq_sdk.consumer.base_consumer import BaseConsumer
from rabbitmq_sdk.enums.event import Event
from rabbitmq_sdk.event.base_event import BaseEvent
from rabbitmq_sdk.event.impl.devices_manager.alarm_waiting import AlarmWaiting

from app.services.audio.audio_service import AudioService


class AlarmWaitingConsumer(BaseConsumer):
    def __init__(self, audio_service: AudioService):
        super().__init__()
        self.audio_service = audio_service

    def get_event(self) -> Event:
        return Event.ALARM_STOPPED

    def event_class(self) -> Type[BaseEvent]:
        return AlarmWaiting

    def do_handle(self, event):
        event: AlarmWaiting = AlarmWaiting.from_dict(event)
        try:
            self.audio_service.start_waiting_audio()
        except:
            pass