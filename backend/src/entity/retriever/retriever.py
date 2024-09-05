from abc import ABC, abstractmethod
from collections.abc import Iterator

import faiss
import numpy as np
import torch

from src.aliases import Candidate
from src.entity.embedder import Modality
from src.entity.retriever.utils import build_faiss_index, build_milvus_collection


class ISearchIteratorFactory(ABC):
    # TODO change signature
    @abstractmethod
    def create_iterator(
        self, embedding: np.ndarray, modalities: list[Modality], batch_size: int
    ) -> Iterator[list[Candidate]]:
        pass


class FaissSearchIteratorFactory(ISearchIteratorFactory):
    def __init__(self, embeddings: np.ndarray, labels: list[str], device: str = "cpu"):
        self._labels = labels
        self._index = build_faiss_index(embeddings, device=device)
        self._device = device

    def retrieve(self, embedding: np.ndarray, modalities: list[Modality], k: int = 32) -> list[Candidate]:
        embedding = embedding.reshape(1, -1).astype(np.float32)
        if self._device != "cpu":
            embedding = torch.tensor(embedding).to(self._device)

        faiss.normalize_L2(embedding)
        distances, indices = self._index.search(embedding, k)  # noqa
        # TODO back compitability with milvus, add modality
        return [(self._labels[i], 1 - distances[0][j]) for j, i in enumerate(indices[0])]


class MilvusSearchIteratorFactory(ISearchIteratorFactory):
    def __init__(
        self,
        index_name: str,
        modality_embeddings: dict[Modality, np.ndarray],
        embeddings_dim: int,
        labels: list[str],
    ):
        self._collection = build_milvus_collection(
            index_name, modality_embeddings=modality_embeddings, embeddings_dim=embeddings_dim, labels=labels
        )
        self._available_modalities = set(modality_embeddings.keys())

    def create_iterator(
        self, embedding: np.ndarray, modalities: list[Modality], batch_size: int
    ) -> Iterator[list[Candidate]]:
        request_modalities = list(set(modalities) & self._available_modalities)
        if not request_modalities:
            raise ValueError(f"Can not create iterator for selected modalities {modalities}.")

        embedding = embedding.reshape(1, -1).astype(np.float32)
        search_iterator = self._collection.search_iterator(
            embedding,
            anns_field="embedding",
            param={"metric_type": "COSINE"},
            batch_size=batch_size,
            limit=2**10,
            partition_names=request_modalities,
            output_fields=["path", "modality"],
        )

        def _iterator() -> Iterator[list[Candidate]]:
            try:
                while True:
                    hits = search_iterator.next()
                    if not hits:
                        break
                    yield [(hit.path, 1 - hit.distance, hit.modality) for hit in hits]
            finally:
                search_iterator.close()

        return _iterator()
