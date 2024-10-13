import faiss
import numpy as np
from more_itertools import chunked
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections
from pymilvus.orm import db, utility

from src.entity.embedder import Modality
from src.types import Label

# TODO not utils please? Move to utils/retriever?


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
    index_name: str, modality_embeddings: dict[Modality, np.ndarray], embeddings_dim: int, labels: list[Label]
) -> Collection:
    if utility.has_collection(index_name):
        collection = Collection(index_name)
        collection.load()
        return collection

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="start", dtype=DataType.INT64),
        FieldSchema(name="end", dtype=DataType.INT64),
        FieldSchema(name="modality", dtype=DataType.VARCHAR, max_length=32),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embeddings_dim),
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
    return collection
