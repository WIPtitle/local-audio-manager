from typing import Type

from rabbitmq_sdk.consumer.base_consumer import BaseConsumer
from rabbitmq_sdk.enums.event import Event
from rabbitmq_sdk.event.base_event import BaseEvent
from rabbitmq_sdk.event.impl.devices_manager.camera_alarm import CameraAlarm

from app.services.audio.audio_service import AudioService


class CameraAlarmConsumer(BaseConsumer):
    def __init__(self, audio_service: AudioService):
        super().__init__()
        self.audio_service = audio_service

    def get_event(self) -> Event:
        return Event.CAMERA_ALARM

    def event_class(self) -> Type[BaseEvent]:
        return CameraAlarm

    def do_handle(self, event):
        event: CameraAlarm = CameraAlarm.from_dict(event)
        print("STARTING AUDIO")
        try:
            self.audio_service.start_audio()
        except:
            pass