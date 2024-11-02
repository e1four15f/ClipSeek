from abc import ABC, abstractmethod

from src.entity.embedder.base import Modality
from src.types import CandidateWithCollection, Collection


class ISearcher(ABC):
    @abstractmethod
    def search(
        self,
        embedding: list[float],
        collections: list[Collection],
        modalities: list[Modality],
        batch_size: int = 32,
    ) -> tuple[list[CandidateWithCollection], str]:
        pass

    @abstractmethod
    def next(self, session_id: str) -> list[CandidateWithCollection]:
        pass
