import os
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette.responses import FileResponse


class IResourcesHandler(ABC):
    @abstractmethod
    async def get_resource(self, file_path: str) -> FileResponse:
        pass


class ResourcesHandler(IResourcesHandler):
    def __init__(self, data_path: str) -> None:
        self._data_path = data_path

    async def get_resource(self, file_path: str) -> FileResponse:
        full_path = os.path.join(self._data_path, file_path)
        if os.path.exists(full_path):
            return FileResponse(full_path)
        raise HTTPException(status_code=404, detail="File not found")
