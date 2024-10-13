from dataclasses import dataclass
from typing import TypedDict

from src.entity.embedder import Modality


@dataclass(frozen=True)
class Collection:
    dataset: str
    version: str

    def __hash__(self) -> int:
        return hash((self.dataset, self.version))


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
