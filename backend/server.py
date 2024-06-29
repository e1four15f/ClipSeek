import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic.v1 import BaseSettings


class AppSettings(BaseSettings):
    data_path: str = '/Users/v.karmazin/repos/diploma/'  # TODO data and paths


class AppServer:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._app = FastAPI()
        self._add_routes()

    def _add_routes(self) -> None:
        self._app.get("/resources/{file_path:path}")(self._get_resource)

    def _get_resource(self, file_path: str) -> FileResponse:
        full_path = os.path.join(self._settings.data_path, file_path)
        if os.path.exists(full_path):
            return FileResponse(full_path)
        raise HTTPException(status_code=404, detail="File not found")

    def create_application(self) -> FastAPI:
        return self._app


def get_app() -> FastAPI:
    return AppServer(settings=AppSettings()).create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_app(), host="localhost", port=8500)
