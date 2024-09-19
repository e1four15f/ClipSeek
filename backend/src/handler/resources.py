import asyncio
import mimetypes
import os
import random
import subprocess
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException, Path, Query
from starlette.responses import FileResponse

from src.aliases import Collection, Dataset, Version


class IResourcesHandler(ABC):
    @abstractmethod
    async def get_raw(self, dataset: Dataset, version: Version, file_path: str) -> FileResponse:
        pass

    @abstractmethod
    async def get_thumbnail(
        self, dataset: Dataset, version: Version, file_path: str, time: Optional[int]
    ) -> FileResponse:
        pass

    @abstractmethod
    async def get_clip(self, dataset: Dataset, version: Version, file_path: str, start: int, end: int) -> FileResponse:
        pass


class ResourcesHandler(IResourcesHandler):
    def __init__(self, dataset_paths: dict[Collection, str]) -> None:
        self._dataset_paths = dataset_paths

    async def get_raw(
        self,
        dataset: str = Path(..., description="The dataset name or identifier"),
        version: str = Path(..., description="The version of the dataset"),
        file_path: str = Path(..., description="The path of the file within the dataset"),
    ) -> FileResponse:
        full_path = os.path.join(self._dataset_paths[(dataset, version)], file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        if full_path.endswith(".mp4"):
            return FileResponse(full_path)

        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type and mime_type.startswith("video"):
            # Convert any video to MP4 format
            tmp_mp4_path = f".tmp/{random.randint(0, 100)}.mp4"
            command = [
                "ffmpeg",
                "-y",
                "-i",
                full_path,
                "-c:v",
                "libx264",
                "-crf",
                "23",
                "-preset",
                "medium",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                tmp_mp4_path,
            ]
            try:
                process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    raise HTTPException(status_code=422, detail=f"Error converting video: {stderr.decode()}")

                return FileResponse(tmp_mp4_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error converting video: {str(e)}")
        return FileResponse(full_path)

    async def get_thumbnail(
        self,
        dataset: str = Path(..., description="The dataset name or identifier"),
        version: str = Path(..., description="The version of the dataset"),
        file_path: str = Path(..., description="The path of the file within the dataset"),
        time: Optional[int] = Query(None, description="Time (in seconds) to extract the thumbnail from"),
    ) -> FileResponse:
        full_path = os.path.join(self._dataset_paths[(dataset, version)], file_path)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        os.makedirs(".tmp", exist_ok=True)
        tmp_image_path = f".tmp/{random.randint(0, 100)}.jpg"

        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type and mime_type.startswith("video"):
            command = ["ffmpeg", "-y"]
            if time is not None:
                command += ["-ss", str(time)]
            command += [
                "-i",
                full_path,
                "-vf",
                "thumbnail,scale=320:-1",
                "-frames:v",
                "1",
                tmp_image_path,
            ]
        else:
            command = [
                "ffmpeg",
                "-y",
                "-i",
                full_path,
                "-vf",
                "scale=320:-1",
                tmp_image_path,
            ]
        try:
            process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise HTTPException(status_code=422, detail=f"Error extracting thumbnail: {stderr.decode()}")
            return FileResponse(tmp_image_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting thumbnail: {str(e)}")

    async def get_clip(
        self,
        dataset: str = Path(..., description="The dataset name or identifier"),
        version: str = Path(..., description="The version of the dataset"),
        file_path: str = Path(..., description="The path of the file within the dataset"),
        start: int = Query(..., description="Clip start time in seconds"),
        end: int = Query(..., description="Clip end time in seconds"),
    ) -> FileResponse:
        full_path = os.path.join(self._dataset_paths[(dataset, version)], file_path)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        os.makedirs(".tmp", exist_ok=True)
        tmp_file_path = f".tmp/{random.randint(0, 100)}.mp4"
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
        try:
            process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise HTTPException(status_code=422, detail=f"Error processing video: {stderr.decode()}")
            return FileResponse(tmp_file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
