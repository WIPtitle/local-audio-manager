from typing import Type

from rabbitmq_sdk.consumer.base_consumer import BaseConsumer
from rabbitmq_sdk.enums.event import Event
from rabbitmq_sdk.event.base_event import BaseEvent
from rabbitmq_sdk.event.impl.devices_manager.reed_alarm import ReedAlarm

from app.services.audio.audio_service import AudioService


class ReedAlarmConsumer(BaseConsumer):
    def __init__(self, audio_service: AudioService):
        super().__init__()
        self.audio_service = audio_service

    def get_event(self) -> Event:
        return Event.REED_ALARM

    def event_class(self) -> Type[BaseEvent]:
        return ReedAlarm

    def do_handle(self, event):
        event: ReedAlarm = ReedAlarm.from_dict(event)
        print("STARTING AUDIO")
        try:
            self.audio_service.start_audio()
        except:
            pass