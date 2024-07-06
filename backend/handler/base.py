from abc import ABC, abstractmethod

from pydantic import BaseModel
from starlette.responses import FileResponse


class SearchRequest(BaseModel):
    query: str
    modalities: list[str]
    datasets: list[int]


class SearchResult(BaseModel):
    dataset: str
    version: str
    path: str
    score: float
    modality: str
    # TODO span
    # TODO extra or extra in resources route?


class SearchResponse(BaseModel):
    data: list[SearchResult]
    hits: int


class ISearchHandler(ABC):
    @abstractmethod
    def search_by_text(self, query: str) -> SearchResponse:
        pass


class IResourcesHandler(ABC):
    @abstractmethod
    def get_resource(self, file_path: str) -> FileResponse:
        pass
