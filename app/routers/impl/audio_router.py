from fastapi import UploadFile, File, Response
from fastapi.responses import FileResponse

from app.config.bindings import inject
from app.routers.router_wrapper import RouterWrapper
from app.services.audio.audio_service import AudioService


class AudioRouter(RouterWrapper):
    @inject
    def __init__(self, audio_service: AudioService):
        super().__init__(prefix=f"/local-audio")
        self.audio_service = audio_service


    def _define_routes(self):
        @self.router.post("/")
        async def save_audio(audio: UploadFile = File(...)):
            self.audio_service.create_audio(audio)
            return Response(status_code=204)


        @self.router.get("/")
        def get_audio() -> FileResponse:
            path = self.audio_service.get_audio()
            return FileResponse(path=path, filename=path.name)


        @self.router.put("/play")
        async def play():
            self.audio_service.start_audio()
            return Response(status_code=204)


        @self.router.put("/stop")
        async def stop():
            self.audio_service.stop_audio()
            return Response(status_code=204)
