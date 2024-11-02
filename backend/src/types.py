from dataclasses import dataclass
from typing import Any, TypedDict

from src.entity.embedder.base import Modality


@dataclass(frozen=True)
class Collection:
    dataset: str
    version: str

    def __hash__(self) -> int:
        return hash((self.dataset, self.version))

    def __eq__(self, other: Any) -> bool:  # noqa: ANN401
        if isinstance(other, tuple):
            return (self.dataset, self.version) == other
        if isinstance(other, Collection):
            return (self.dataset, self.version) == (other.dataset, other.version)
        return NotImplemented


@dataclass(frozen=True)
class Candidate:
    id: int
    path: str
    score: float
    modality: Modality
    span: tuple[int, int]


@dataclass(frozen=True)
class CandidateWithCollection(Candidate, Collection):
    pass


class Label(TypedDict):
    path: str
    span: tuple[int, int]


@dataclass(frozen=True)
class IndexedEntity:
    id: int
    path: str
    span: tuple[int, int]
    modality: Modality
    embedding: list[float]


@dataclass(frozen=True)
class CollectionEntity:
    name: str
    partitions: list[str]
    row_count: int
