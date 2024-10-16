from abc import ABC, abstractmethod

from pymilvus import MilvusClient

from src.entity.embedder import Modality
from src.types import CollectionEntity, IndexedEntity


class IStorage(ABC):
    @abstractmethod
    def get_by_id(self, id: str, dataset: str, version: str) -> IndexedEntity:
        pass

    @abstractmethod
    def get_collections(self) -> list[CollectionEntity]:
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

    def get_collections(self) -> list[CollectionEntity]:
        collections = self._client.list_collections()
        collection_entities = []
        for collection in collections:
            partitions = self._client.list_partitions(collection_name=collection)
            collection_stats = self._client.get_collection_stats(collection_name=collection)
            collection_entities.append(
                CollectionEntity(
                    name=collection,
                    partitions=[partition for partition in partitions if partition != "_default"],
                    row_count=collection_stats["row_count"],
                )
            )
        return collection_entities
