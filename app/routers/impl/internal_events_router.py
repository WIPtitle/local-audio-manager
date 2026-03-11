from fastapi import Response
from pydantic import BaseModel

from app.config.bindings import inject
from app.routers.router_wrapper import RouterWrapper
from app.services.audio.audio_service import AudioService


class AlarmWaitingRequest(BaseModel):
    started: bool
    duration: int | None = None


class SensorAlarmRequest(BaseModel):
    sensor_name: str
    duration: int | None = None


class MotionWarningRequest(BaseModel):
    camera_name: str


class InternalEventsRouter(RouterWrapper):
    @inject
    def __init__(self, audio_service: AudioService):
        super().__init__(prefix="/internal/alarm")
        self.audio_service = audio_service

    def _define_routes(self):
        @self.router.post("/sensor-alarm")
        def on_sensor_alarm(request: SensorAlarmRequest):
            self.audio_service.start_audio(duration=request.duration)
            return Response(status_code=204)

        @self.router.post("/waiting")
        def on_alarm_waiting(request: AlarmWaitingRequest):
            if request.started:
                self.audio_service.start_waiting_audio(duration=request.duration)
            else:
                self.audio_service.stop_audio()
            return Response(status_code=204)

        @self.router.post("/stopped")
        def on_alarm_stopped():
            self.audio_service.stop_audio()
            return Response(status_code=204)

        @self.router.post("/motion-warning")
        def on_motion_warning(request: MotionWarningRequest):
            self.audio_service.start_warning_audio()
            return Response(status_code=204)
