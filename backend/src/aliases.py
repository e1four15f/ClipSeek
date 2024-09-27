from typing import TypedDict

from src.entity.embedder import Modality

Version = str
Dataset = str
Collection = tuple[Dataset, Version]

Id = int
Score = float
Path = str
Span = tuple[int, int]
Candidate = tuple[Id, Path, Score, Modality, Span]
CandidateWithCollection = tuple[Candidate, Collection]


class Label(TypedDict):
    path: str
    span: tuple[int, int]
