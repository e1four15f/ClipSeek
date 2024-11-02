from abc import ABC, abstractmethod
from enum import Enum

from src.types import CollectionEntity, IndexedEntity


class StorageType(str, Enum):
    MILVUS = "Milvus"
    FAISS = "FAISS"


class IStorage(ABC):
    @abstractmethod
    def get_by_id(self, id: str, dataset: str, version: str) -> IndexedEntity:
        pass

    @abstractmethod
    def get_collections(self) -> list[CollectionEntity]:
        pass
