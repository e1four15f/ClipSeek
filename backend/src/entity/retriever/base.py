from abc import ABC, abstractmethod
from collections.abc import Iterator

from src.entity.embedder.base import Modality
from src.types import Candidate


class ISearchIteratorFactory(ABC):
    @abstractmethod
    def create_iterator(
        self, embedding: list[float], modalities: list[Modality], batch_size: int
    ) -> Iterator[list[Candidate]]:
        pass
