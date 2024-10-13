import json
import tempfile
from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, model_validator
from pymilvus import MilvusException
from pymilvus.exceptions import DescribeCollectionException

from src.entity.embedder import IEmbedder, Modality
from src.entity.searcher import BatchSearcher
from src.entity.storage import IStorage
from src.types import CandidateWithCollection, Collection


class SearchConfiguration(BaseModel):
    n_candidates: int = Field(..., description="Number of results to retrieve", examples=[32])
    modalities: list[str] = Field(..., description="List of modalities to use for searching", examples=[["video"]])
    collections: list[dict[str, str]] = Field(
        ...,
        description="List of dataset and version mappings",
        examples=[[{"dataset": "MSRVTT", "version": "train"}, {"dataset": "MSVD", "version": "all"}]],
    )

    @model_validator(mode="before")
    def check_and_parse_config(cls, values: str) -> dict:  # noqa: N805
        if isinstance(values, str):
            try:
                values = json.loads(values)
            except json.JSONDecodeError as e:
                raise ValueError("Invalid JSON format for config") from e
        return values  # type: ignore[return-value]


RequestText = Annotated[
    str, Form(description="Text query for search", examples=["Cat in black suit is having meeting"])
]
RequestFile = Annotated[UploadFile, File(description="File to search for similar")]
RequestID = Annotated[str, Form(description="Reference ID for the search")]
RequestDataset = Annotated[str, Form(description="Reference's dataset for the search")]
RequestVersion = Annotated[str, Form(description="Reference's version for the search")]


class ContinueSearchRequest(BaseModel):
    session_id: str = Field(..., description="The session ID for continuing the search")


class SearchResult(BaseModel):
    id: str = Field(..., description="The unique file ID")
    dataset: str = Field(..., description="The dataset name")
    version: str = Field(..., description="The dataset version")
    path: str = Field(..., description="Relative path to the result file")
    score: float = Field(..., description="Similarity score")
    modality: str = Field(..., description="The modality of the result")
    span: tuple[int, int] = Field(..., description="Start and end seconds of the clip")


class SearchResponse(BaseModel):
    session_id: str = Field(..., description="The session ID of the search")
    hits: int = Field(..., description="The number of search hits")
    data: list[SearchResult] = Field(..., description="The list of search results")


class ISearchHandler(ABC):
    @abstractmethod
    async def search_by_text(self, text: RequestText, config: SearchConfiguration) -> SearchResponse:
        pass

    @abstractmethod
    async def search_by_file(self, file: RequestFile, config: SearchConfiguration) -> SearchResponse:
        pass

    @abstractmethod
    async def search_by_reference(
        self, id: RequestID, dataset: RequestDataset, version: RequestVersion, config: SearchConfiguration
    ) -> SearchResponse:
        pass

    @abstractmethod
    async def continue_search(self, request: ContinueSearchRequest) -> SearchResponse:
        pass


class SearchHandler(ISearchHandler):
    def __init__(
        self,
        embedder: IEmbedder,
        storage: IStorage,
        searcher: BatchSearcher,
    ) -> None:
        self._embedder = embedder
        self._storage = storage
        self._searcher = searcher

    async def search_by_text(self, text: RequestText, config: SearchConfiguration) -> SearchResponse:
        # TODO think about -> torch.Tensor
        text_embedding = self._embedder.embed(text, modality=Modality.TEXT).detach().cpu().tolist()
        return self._try_perform_search(text_embedding, config=config)

    async def search_by_file(self, file: RequestFile, config: SearchConfiguration) -> SearchResponse:
        mime_type = file.content_type
        if mime_type:
            if mime_type.startswith("image/"):
                file_modality = Modality.IMAGE
            elif mime_type.startswith("video/"):
                file_modality = Modality.VIDEO
            elif mime_type.startswith("audio/"):
                file_modality = Modality.AUDIO
            else:
                raise HTTPException(status_code=422, detail=f"Unsupported MIME type: {mime_type}")
        else:
            raise HTTPException(status_code=422, detail="Received file without MIME type")

        with tempfile.NamedTemporaryFile() as tmp_file:
            saved_file_path = tmp_file.name
            tmp_file.write(await file.read())

            # TODO think about -> torch.Tensor
            file_embedding = self._embedder.embed(saved_file_path, modality=file_modality).detach().cpu().tolist()
            return self._try_perform_search(file_embedding, config=config)

    async def search_by_reference(
        self, id: RequestID, dataset: RequestDataset, version: RequestVersion, config: SearchConfiguration
    ) -> SearchResponse:
        try:
            document = self._storage.get_by_id(id=id, dataset=dataset, version=version)
        except DescribeCollectionException as e:
            raise HTTPException(status_code=404, detail=e.message) from e
        except MilvusException as e:
            raise HTTPException(status_code=500, detail=f"Milvus error: {str(e)}") from e
        return self._try_perform_search(document.embedding, config=config)

    def _try_perform_search(self, embedding: list[float], config: SearchConfiguration) -> SearchResponse:
        try:
            candidates, session_id = self._searcher.search(
                embedding=embedding,
                collections=[Collection(dataset=c["dataset"], version=c["version"]) for c in config.collections],
                modalities=[Modality(m) for m in config.modalities],
                batch_size=config.n_candidates,
            )
        except StopIteration as e:
            raise HTTPException(status_code=404, detail="No results found.") from e
        except KeyError as e:
            raise HTTPException(status_code=404, detail=f"{e.args[0]} not found.") from e
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
                    id=str(candidate.id),
                    dataset=candidate.dataset,
                    version=candidate.version,
                    path=candidate.path,
                    score=candidate.score,
                    modality=candidate.modality,
                    span=candidate.span,
                )
                for candidate in candidates
            ],
        )
