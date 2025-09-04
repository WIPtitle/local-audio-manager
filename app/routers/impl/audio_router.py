from fastapi import UploadFile, File, Response, Request
from fastapi.responses import FileResponse

from app.clients.auth_client import AuthClient
from app.config.bindings import inject
from app.exceptions.authorization_exception import AuthorizationException
from app.routers.router_wrapper import RouterWrapper
from app.services.audio.audio_service import AudioService


class AudioRouter(RouterWrapper):
    @inject
    def __init__(self, audio_service: AudioService, auth_client: AuthClient):
        super().__init__(prefix=f"/audio")
        self.audio_service = audio_service
        self.auth_client = auth_client

    def _define_routes(self):
        @self.router.post("/")
        async def save_audio(request: Request, audio: UploadFile = File(...)):
            token = request.headers.get("Authorization")
            user = await self.auth_client.get_authenticated_user(token)
            if user is None or "CHANGE_ALARM_SOUND" not in user.permissions:
                raise AuthorizationException("Not authorized")
            self.audio_service.create_audio(audio)
            return Response(status_code=204)

        @self.router.api_route("/", methods=["GET", "HEAD"])
        def get_audio() -> FileResponse:
            path = self.audio_service.get_audio()
            response = FileResponse(
                path=path,
                filename=path.name,
                media_type="audio/mpeg"
            )
            response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            return response

        @self.router.delete("/")
        async def delete_audio(request: Request):
            token = request.headers.get("Authorization")
            user = await self.auth_client.get_authenticated_user(token)
            if user is None or "CHANGE_ALARM_SOUND" not in user.permissions:
                raise AuthorizationException("Not authorized")
            self.audio_service.delete_audio()
            return Response(status_code=204)