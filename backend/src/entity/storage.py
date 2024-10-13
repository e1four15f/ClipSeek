from abc import ABC, abstractmethod

from pymilvus import MilvusClient

from src.entity.embedder import Modality
from src.types import IndexedEntity


class IStorage(ABC):
    @abstractmethod
    def get_by_id(self, id: str, dataset: str, version: str) -> IndexedEntity:
        pass


class MilvusStorage(IStorage):
    def __init__(self, client: MilvusClient):
        self._client = client

    def get_by_id(self, id: str, dataset: str, version: str) -> IndexedEntity:
        documents = self._client.get(collection_name=f"{dataset}__{version}", ids=[id])
        document = documents[0]
        return IndexedEntity(
            id=document["id"],
            path=document["path"],
            span=(document["start"], document["end"]),
            modality=Modality(document["modality"]),
            embedding=document["embedding"],
        )
