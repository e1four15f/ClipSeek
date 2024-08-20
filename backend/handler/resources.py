import os
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette.responses import FileResponse

from backend.aliases import Collection, Dataset, Version


class IResourcesHandler(ABC):
    @abstractmethod
    async def get_resource(self, dataset: Dataset, version: Version, file_path: str) -> FileResponse:
        pass


class ResourcesHandler(IResourcesHandler):
    def __init__(self, dataset_paths: dict[Collection, str]) -> None:
        self._dataset_paths = dataset_paths

    async def get_resource(self, dataset: Dataset, version: Version, file_path: str) -> FileResponse:
        full_path = os.path.join(self._dataset_paths[(dataset, version)], file_path)
        if os.path.exists(full_path):
            return FileResponse(full_path)
        raise HTTPException(status_code=404, detail="File not found")
