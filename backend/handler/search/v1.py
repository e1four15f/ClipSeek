from abc import ABC, abstractmethod

from fastapi import HTTPException
from pydantic import BaseModel, Field

from backend.aliases import CandidateWithCollection
from backend.entity.embedder import IEmbedder, Modality
from backend.entity.searcher import BatchSearcher


class SearchRequest(BaseModel):
    query: str = Field(..., examples=["Cat in black suit is having meeting"])
    modalities: list[Modality] = Field(..., examples=[["video"]])
    collections: list[dict[str, str]] = Field(
        ..., examples=[[{"dataset": "MSRVTT", "version": "all"}, {"dataset": "MSVD", "version": "5sec"}]]
    )


class SearchNextRequest(BaseModel):
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
    async def search_by_text(self, request: SearchRequest) -> SearchResponse:
        pass

    @abstractmethod
    async def continue_search(self, request: SearchNextRequest) -> SearchResponse:
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

    async def search_by_text(self, request: SearchRequest) -> SearchResponse:
        query_embedding = self._embedder.embed(request.query, modality=Modality.TEXT)
        try:
            candidates, session_id = self._searcher.search(
                embedding=query_embedding.detach().numpy(),
                collections=[(collection["dataset"], collection["version"]) for collection in request.collections],
                modalities=request.modalities,
                batch_size=self._candidates_per_page,
            )
        except StopIteration as e:
            raise HTTPException(status_code=404, detail="No results found.") from e
        return self._build_search_response(
            session_id=session_id,
            candidates=candidates,
        )

    async def continue_search(self, request: SearchNextRequest) -> SearchResponse:
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
