import sys
from typing import Type

from rabbitmq_sdk.consumer.base_consumer import BaseConsumer
from rabbitmq_sdk.enums.event import Event
from rabbitmq_sdk.event.base_event import BaseEvent
from rabbitmq_sdk.event.impl.devices_manager.alarm_stopped import AlarmStopped


class AlarmStoppedConsumer(BaseConsumer):
    def get_event(self) -> Event:
        return Event.ALARM_STOPPED

    def event_class(self) -> Type[BaseEvent]:
        return AlarmStopped

    def do_handle(self, event):
        event = AlarmStopped.from_dict(event)
        print(event.timestamp)
        sys.stdout.flush()