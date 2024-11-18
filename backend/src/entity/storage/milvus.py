
import numpy as np
from more_itertools import chunked
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, MilvusClient, connections
from pymilvus.orm import db

from src.entity.embedder.base import Modality
from src.entity.storage.base import IStorage
from src.types import CollectionEntity, IndexedEntity, Label


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


def create_milvus_connection(url: str, database_name: str = "default") -> None:
    connections.connect(uri=url)
    if database_name not in db.list_database():
        db.create_database(database_name)
    db.using_database(database_name)


def build_milvus_collection(
    index_name: str,
    modality_embeddings: dict[Modality, np.ndarray],
    embeddings_dim: int,
    labels: list[Label],
    index_type: str = "FLAT",
) -> None:
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="start", dtype=DataType.FLOAT),
        FieldSchema(name="end", dtype=DataType.FLOAT),
        FieldSchema(name="modality", dtype=DataType.VARCHAR, max_length=32),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embeddings_dim),
    ]
    collection = Collection(name=index_name, schema=CollectionSchema(fields, enable_dynamic_field=False))
    index_params = {
        "metric_type": "COSINE",
        "index_type": index_type,
    }
    if index_type == 'IVF_FLAT':
        index_params["nlist"] = 1024
    collection.create_index("embedding", index_params)

    collection.load()
    for modality, embeddings in modality_embeddings.items():
        collection.create_partition(partition_name=modality)
        entities = (
            {
                "path": label["path"],
                "start": (label.get("span") or [0, 0])[0],
                "end": (label.get("span") or [0, 0])[1],
                "embedding": embedding,
                "modality": modality,
            }
            for embedding, label in zip(embeddings, labels)
        )
        for batch in chunked(entities, 10_000):  # setting limit fix gRPC resource exhausted error
            collection.insert(batch, partition_name=modality)
