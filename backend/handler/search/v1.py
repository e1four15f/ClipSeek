import json
import tempfile
from abc import ABC, abstractmethod
from typing import Annotated

import numpy as np
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, model_validator

from backend.aliases import CandidateWithCollection
from backend.entity.embedder import IEmbedder, Modality
from backend.entity.searcher import BatchSearcher


class SearchConfiguration(BaseModel):
    modalities: list[Modality] = Field(..., examples=[["video"]])
    collections: list[dict[str, str]] = Field(
        ..., examples=[[{"dataset": "MSRVTT", "version": "all"}, {"dataset": "MSVD", "version": "5sec"}]]
    )

    @model_validator(mode="before")
    def check_and_parse_config(cls, values):
        if isinstance(values, str):
            try:
                values = json.loads(values)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for config")
        return values


RequestText = Annotated[str, Form(examples=["Cat in black suit is having meeting"])]
RequestFile = Annotated[UploadFile, File()]


class ContinueSearchRequest(BaseModel):
    session_id: str


class SearchResult(BaseModel):
    dataset: str
    version: str
    path: str
    score: float
    modality: str
    # TODO span
    # TODO extra or extra in resources route?


class SearchResponse(BaseModel):
    session_id: str
    hits: int
    data: list[SearchResult]


class ISearchHandler(ABC):
    @abstractmethod
    async def search_by_text(self, text: RequestText, config: SearchConfiguration) -> SearchResponse:
        pass

    @abstractmethod
    async def search_by_file(self, file: RequestFile, config: SearchConfiguration) -> SearchResponse:
        pass

    @abstractmethod
    async def continue_search(self, request: ContinueSearchRequest) -> SearchResponse:
        pass


class SearchHandler(ISearchHandler):
    def __init__(
        self,
        embedder: IEmbedder,
        retriever: BatchSearcher,
        candidates_per_page: int,
    ) -> None:
        self._embedder = embedder
        self._searcher = retriever
        self._candidates_per_page = candidates_per_page

    async def search_by_text(self, text: RequestText, config: SearchConfiguration) -> SearchResponse:
        text_embedding = self._embedder.embed(text, modality=Modality.TEXT).detach().numpy()
        return self._try_perform_search(text_embedding, config=config)

    async def search_by_file(self, file: RequestFile, config: SearchConfiguration) -> SearchResponse:
        mime_type = file.content_type
        if mime_type.startswith("image/"):
            file_modality = Modality.IMAGE
        elif mime_type.startswith("video/"):
            file_modality = Modality.VIDEO
        elif mime_type.startswith("audio/"):
            file_modality = Modality.AUDIO
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

        with tempfile.NamedTemporaryFile() as tmp_file:
            saved_file_path = tmp_file.name
            tmp_file.write(await file.read())

            file_embedding = self._embedder.embed(saved_file_path, modality=file_modality).detach().numpy()
            return self._try_perform_search(file_embedding, config=config)

    def _try_perform_search(self, embedding: np.ndarray, config: SearchConfiguration):
        try:
            candidates, session_id = self._searcher.search(
                embedding=embedding,
                collections=[(collection["dataset"], collection["version"]) for collection in config.collections],
                modalities=config.modalities,
                batch_size=self._candidates_per_page,
            )
        except StopIteration as e:
            raise HTTPException(status_code=404, detail="No results found.") from e
        return self._build_search_response(
            session_id=session_id,
            candidates=candidates,
        )

    async def continue_search(self, request: ContinueSearchRequest) -> SearchResponse:
        try:
            candidates = self._searcher.next(request.session_id)
        except StopIteration as e:
            raise HTTPException(status_code=204, detail="Continue limit reached.") from e
        except KeyError as e:
            raise HTTPException(status_code=404, detail="Recieved unknown session_id.") from e
        return self._build_search_response(
            session_id=request.session_id,
            candidates=candidates,
        )

    def _build_search_response(self, session_id: str, candidates: list[CandidateWithCollection]) -> SearchResponse:
        return SearchResponse(
            session_id=session_id,
            hits=len(candidates),
            data=[
                SearchResult(
                    dataset=dataset,
                    version=version,
                    path=path,
                    score=score,
                    modality=modality,
                )
                for ((path, score, modality), (dataset, version)) in candidates
            ],
        )
