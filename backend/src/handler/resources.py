import asyncio
import logging
import mimetypes
import os
import pathlib
import subprocess
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Optional

from fastapi import HTTPException, Path, Query
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import FileResponse, Response, StreamingResponse

from src.config import Config
from src.types import Collection
from src.utils.docstring import DocstringMixin
from src.utils.streaming import build_streaming_response

logger = logging.getLogger(__name__)


class IResourcesHandler(ABC, DocstringMixin):
    @abstractmethod
    async def get_raw(self, request: Request, dataset: str, version: str, file_path: str) -> Response:
        """Retrieves the original media file from the specified dataset, converting it to MP4 format if necessary."""

    @abstractmethod
    async def get_thumbnail(
        self, request: Request, dataset: str, version: str, file_path: str, time: Optional[float]
    ) -> Response:
        """Cuts a clip from the specified video based on the defined start and end times."""

    @abstractmethod
    async def get_clip(
        self, request: Request, dataset: str, version: str, file_path: str, start: float, end: float
    ) -> Response:
        """Extracts a thumbnail image from a specified time and scales it to 320 pixels wide."""


class ResourcesHandler(IResourcesHandler):
    def __init__(self, dataset_paths: dict[Collection, str], indexes_path: pathlib.Path) -> None:
        self._dataset_paths = dataset_paths
        self._indexes_path = indexes_path

    async def get_raw(
        self,
        request: Request,
        dataset: str = Path(..., description="The dataset name or identifier"),
        version: str = Path(..., description="The version of the dataset"),
        file_path: str = Path(..., description="The file's path within the dataset"),
    ) -> Response:
        content_type = "video/mp4"
        full_path = self._get_full_path(file_path, dataset, version)

        if full_path.endswith(".mp4"):  # TODO: Just mp4? maybe other formats also work?
            file_size = os.stat(full_path).st_size
            return build_streaming_response(
                request,
                stream=open(full_path, "rb"),  # noqa: SIM115
                file_size=file_size,
                content_type=content_type,
            )

        tmp_mp4_path = f"{Config.TMP_DIR}/{hash(('raw', full_path))}.mp4"
        if os.path.exists(tmp_mp4_path):
            file_size = os.stat(tmp_mp4_path).st_size
            return build_streaming_response(
                request,
                stream=open(tmp_mp4_path, "rb"),  # noqa: SIM115
                file_size=file_size,
                content_type=content_type,
            )

        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type and mime_type.startswith("video"):
            # Convert any video to MP4 format
            command = [
                "ffmpeg", "-y",
                "-i", full_path,
                "-c:v", "libx264",
                "-crf", "23",
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "192k",
                tmp_mp4_path,
            ]  # fmt: skip
            try:
                process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    raise HTTPException(status_code=422, detail=f"Error converting video: {stderr.decode()}")

                file_size = os.stat(tmp_mp4_path).st_size
                return build_streaming_response(
                    request,
                    stream=open(tmp_mp4_path, "rb"),  # noqa: SIM115
                    file_size=file_size,
                    content_type=content_type,
                    background=_file_cleanup_task(tmp_mp4_path),
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error converting video: {str(e)}") from e
        # for images  # TODO what about audio?
        return FileResponse(full_path)

    async def get_thumbnail(
        self,
        request: Request,  # noqa: ARG002
        dataset: str = Path(..., description="The dataset name or identifier"),
        version: str = Path(..., description="The version of the dataset"),
        file_path: str = Path(..., description="The file's path within the dataset"),
        time: Optional[float] = Query(None, description="Time (in seconds) to extract the thumbnail from"),
    ) -> Response:
        full_path = self._get_full_path(file_path, dataset, version)

        if time is None:
            cache_path = self._indexes_path / dataset / version / "thumbnails" / (file_path + ".jpg")
        else:
            cache_path = self._indexes_path / dataset / version / "thumbnails" / (file_path + "." + str(time) + ".jpg")
        if cache_path.exists():
            return FileResponse(cache_path, headers={"X-CACHED": "true"})

        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type and mime_type.startswith("video"):
            command = ["ffmpeg", "-y"]
            if time is not None:
                command += ["-ss", str(time)]
            command += [
                "-i", full_path,
                "-vf", "thumbnail,scale=320:-1",
                "-frames:v", "1",
                "-f", "image2pipe",
                "-vcodec", "mjpeg",
                "pipe:1",
            ]  # fmt: skip
        else:
            command = [
                "ffmpeg", "-y",
                "-i", full_path,
                "-vf", "scale=320:-1",
                "-f", "image2pipe",
                "-vcodec", "mjpeg",
                "pipe:1",
            ]  # fmt: skip

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise HTTPException(status_code=422, detail=f"Error extracting thumbnail: {stderr.decode()}")

            image_bytes = BytesIO(stdout)
            return StreamingResponse(image_bytes, media_type="image/jpeg")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting thumbnail: {str(e)}") from e

    async def get_clip(
        self,
        request: Request,
        dataset: str = Path(..., description="The dataset name or identifier"),
        version: str = Path(..., description="The version of the dataset"),
        file_path: str = Path(..., description="The file's path within the dataset"),
        start: float = Query(..., description="Clip start time in seconds"),
        end: float = Query(..., description="Clip end time in seconds"),
    ) -> Response:
        content_type = "video/mp4"
        full_path = self._get_full_path(file_path, dataset, version)

        tmp_file_path = f"{Config.TMP_DIR}/{hash(('clip', full_path))}.mp4"
        if os.path.exists(tmp_file_path):
            file_size = os.stat(tmp_file_path).st_size
            return build_streaming_response(
                request,
                stream=open(tmp_file_path, "rb"),  # noqa: SIM115
                file_size=file_size,
                content_type=content_type,
            )

        command = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", full_path,
            "-t", str(end - start),
            "-c", "copy",
            # "-movflags", "faststart",
            tmp_file_path,
        ]  # fmt: skip
        try:
            process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise HTTPException(status_code=422, detail=f"Error processing video: {stderr.decode()}")

            file_size = os.stat(tmp_file_path).st_size
            return build_streaming_response(
                request,
                stream=open(tmp_file_path, "rb"),  # noqa: SIM115
                file_size=file_size,
                content_type=content_type,
                background=_file_cleanup_task(tmp_file_path),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}") from e

    def _get_full_path(self, file_path: str, dataset: str, version: str) -> str:
        try:
            full_path = os.path.join(self._dataset_paths[Collection(dataset=dataset, version=version)], file_path)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=f"{e.args[0]} not found.") from e
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        return full_path


def _file_cleanup_task(file_path: str) -> BackgroundTask:
    """Cleanup function to close and delete the file after streaming"""

    async def _inner() -> None:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning("Error deleting file: %s", e)

    return _inner  # type: ignore[return-value]
