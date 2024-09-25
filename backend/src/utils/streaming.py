from collections.abc import Iterable
from http import HTTPStatus
from typing import BinaryIO

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import StreamingResponse


def build_streaming_response(
    request: Request, stream: BinaryIO, file_size: int, content_type: str
) -> StreamingResponse:
    range_header = request.headers.get("range")
    start, end = 0, file_size - 1

    if range_header:
        try:
            start, end = (int(x) if x else None for x in range_header.replace("bytes=", "").split("-"))
            start = start or 0
            end = end or file_size - 1
        except ValueError as e:
            raise HTTPException(
                HTTPStatus.PARTIAL_CONTENT, detail=f"Invalid request range (Range:{range_header!r})"
            ) from e
        if start > end or start < 0 or end >= file_size:
            raise HTTPException(HTTPStatus.PARTIAL_CONTENT, detail=f"Invalid request range (Range:{range_header!r})")

    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(end - start + 1),
        "content-range": f"bytes {start}-{end}/{file_size}",
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, " "content-range, content-encoding"
        ),
    }

    return StreamingResponse(
        send_bytes_range_requests(stream, start, end),
        headers=headers,
        status_code=HTTPStatus.PARTIAL_CONTENT if range_header else HTTPStatus.OK,
        media_type=content_type,
    )


def send_bytes_range_requests(file_obj: BinaryIO, start: int, end: int, chunk_size: int = 10_000) -> Iterable[bytes]:
    with file_obj as f:
        f.seek(start)
        while (pos := f.tell()) <= end:
            read_size = min(chunk_size, end + 1 - pos)
            yield f.read(read_size)
