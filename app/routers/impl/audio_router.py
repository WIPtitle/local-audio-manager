from fastapi import UploadFile, File, Response
from fastapi.responses import FileResponse

from app.config.bindings import inject
from app.routers.router_wrapper import RouterWrapper
from app.services.audio.audio_service import AudioService


class AudioRouter(RouterWrapper):
    @inject
    def __init__(self, audio_service: AudioService):
        super().__init__(prefix=f"/audio")
        self.audio_service = audio_service


    def _define_routes(self):
        @self.router.post("/")
        async def save_audio(audio: UploadFile = File(...)):
            self.audio_service.create_audio(audio)
            return Response(status_code=204)


        @self.router.get("/")
        def get_audio() -> FileResponse:
            path = self.audio_service.get_audio()
            response = FileResponse(path=path, filename=path.name)
            response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            return response


        @self.router.delete("/")
        def delete_audio():
            self.audio_service.delete_audio()
            return Response(status_code=204)
