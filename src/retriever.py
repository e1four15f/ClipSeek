from abc import ABC, abstractmethod

import faiss
import numpy as np
import torch
from more_itertools import chunked
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections
from pymilvus.orm import db, utility

from src.config import EMBEDDINGS_DIM, MILVUS_DB_NAME, MILVUS_URL
from src.embedder import Modality


class IRetriever(ABC):
    @abstractmethod
    def retrieve(self, embedding: np.ndarray, modalities: list[Modality], k: int = 32) -> list[tuple[str, float]]:
        pass


class FaissMediaRetriever(IRetriever):
    def __init__(self, embeddings: np.ndarray, labels: list[str], device: str = "cpu"):
        self._labels = labels
        self._index = build_faiss_index(embeddings, device=device)
        self._device = device

    def retrieve(self, embedding: np.ndarray, modalities: list[Modality], k: int = 32) -> list[tuple[str, float]]:
        embedding = embedding.reshape(1, -1).astype(np.float32)
        if self._device != "cpu":
            embedding = torch.tensor(embedding).to(self._device)

        faiss.normalize_L2(embedding)
        distances, indices = self._index.search(embedding, k)  # noqa
        return [(self._labels[i], 1 - distances[0][j]) for j, i in enumerate(indices[0])]


class MilvusMediaRetriever(IRetriever):
    def __init__(
        self, index_name: str, modality_embeddings: dict[Modality, np.ndarray], labels: list[str], device: str = "cpu"
    ):
        create_milvus_connection(url=MILVUS_URL, database_name=MILVUS_DB_NAME)
        self._collection = build_milvus_collection(index_name, modality_embeddings=modality_embeddings, labels=labels)
        self._device = device
        self._available_modalities = set(modality_embeddings.keys())

    def retrieve(self, embedding: np.ndarray, modalities: list[Modality], k: int = 32) -> list[tuple[str, float]]:
        embedding = embedding.reshape(1, -1).astype(np.float32)
        if self._device != "cpu":
            embedding = torch.tensor(embedding).to(self._device)

        request_modalities = list(set(modalities) & self._available_modalities)
        if not request_modalities:
            return []

        results = self._collection.search(
            embedding,
            anns_field="embedding",
            param={
                "metric_type": "COSINE",
            },
            limit=k,
            partition_names=request_modalities,
            output_fields=["path", "modality"],
        )
        hits = results[0]
        return [(hit.path, 1 - hit.distance, hit.modality) for hit in hits]


class MultipleRetrievers:
    def __init__(self, retrievers: list[IRetriever]):
        self._retrievers = retrievers

    def retrieve(
        self, embedding: np.ndarray, modalities: list[str], ignore_retrievers: list[int], k: int = 32
    ) -> list[tuple[str, float]]:
        results = []
        for retriever, is_enabled in zip(self._retrievers, ignore_retrievers):
            if is_enabled:
                results += retriever.retrieve(embedding, modalities=modalities, k=k)

        results.sort(key=lambda x: x[1], reverse=False)
        return results[:k]


def build_faiss_index(embeddings: np.ndarray, device: str = "cpu") -> faiss.IndexFlatIP:
    index = faiss.IndexFlatIP(embeddings.shape[1])
    if device != "cpu":
        index = faiss.index_cpu_to_all_gpus(index)

    embeddings = embeddings.astype(np.float32)
    for batch in chunked(embeddings, 10_000):  # setting limit fix malloc_error_break on macOS
        batch = np.stack(batch)  # noqa
        faiss.normalize_L2(batch)
        index.add(batch)  # noqa
    return index


def create_milvus_connection(url: str, database_name: str = "default") -> None:
    connections.connect(uri=url)
    if database_name not in db.list_database():
        db.create_database(database_name)
    db.using_database(database_name)


def build_milvus_collection(
    index_name: str, modality_embeddings: dict[Modality, np.ndarray], labels: list[str]
) -> Collection:
    if utility.has_collection(index_name):
        collection = Collection(index_name)
        collection.load()
        return collection

    # TODO SPAN
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="modality", dtype=DataType.VARCHAR, max_length=32),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDINGS_DIM),
    ]
    collection = Collection(name=index_name, schema=CollectionSchema(fields, enable_dynamic_field=False))
    index_params = {
        "metric_type": "COSINE",
        "index_type": "FLAT",  # "IVF_FLAT",  # TODO AKNN
        # "params": {"nlist": 128},
    }
    collection.create_index("embedding", index_params)

    collection.load()
    for modality, embeddings in modality_embeddings.items():
        collection.create_partition(partition_name=modality)
        entities = (
            {"path": label, "embedding": embedding, "modality": modality}
            for embedding, label in zip(embeddings, labels)
        )
        for batch in chunked(entities, 10_000):  # setting limit fix gRPC resource exhausted error
            collection.insert(batch, partition_name=modality)
    return collection
