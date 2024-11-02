from abc import ABC, abstractmethod

from src.types import CollectionEntity, IndexedEntity


class IStorage(ABC):
    @abstractmethod
    def get_by_id(self, id: str, dataset: str, version: str) -> IndexedEntity:
        pass

    @abstractmethod
    def get_collections(self) -> list[CollectionEntity]:
        pass
