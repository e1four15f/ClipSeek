import asyncio
import os
import random
import subprocess
from abc import ABC, abstractmethod

from fastapi import HTTPException, Query
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse

from src.aliases import Collection, Dataset, Version


class IResourcesHandler(ABC):
    @abstractmethod
    async def get_resource(self, dataset: Dataset, version: Version, file_path: str) -> FileResponse:
        pass

    @abstractmethod
    async def get_clip(
        self, dataset: Dataset, version: Version, file_path: str, span: tuple[int, int]
    ) -> StreamingResponse:
        pass


class ResourcesHandler(IResourcesHandler):
    def __init__(self, dataset_paths: dict[Collection, str]) -> None:
        self._dataset_paths = dataset_paths

    async def get_resource(self, dataset: Dataset, version: Version, file_path: str) -> FileResponse:
        full_path = os.path.join(self._dataset_paths[(dataset, version)], file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(full_path)

    async def get_clip(
        self,
        dataset: Dataset,
        version: Version,
        file_path: str,
        start: int = Query(..., description="Clip start time in seconds"),
        end: int = Query(..., description="Clip end time in seconds"),
    ) -> FileResponse:
        full_path = os.path.join(self._dataset_paths[(dataset, version)], file_path)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        os.makedirs(".tmp", exist_ok=True)
        tmp_file_path = f".tmp/{random.randint(0, 100)}.mp4"
        try:
            with open(tmp_file_path, "w"):
                command = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    full_path,
                    "-ss",
                    str(start),
                    "-t",
                    str(end - start),
                    "-c",
                    "copy",
                    tmp_file_path,
                ]
                process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    raise HTTPException(status_code=422, detail=f"Error processing video: {stderr.decode()}")
                return FileResponse(tmp_file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
