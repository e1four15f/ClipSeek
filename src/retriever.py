from abc import ABC

import numpy as np
import faiss
import torch
from more_itertools import chunked


class IRetriever(ABC):
    def retrieve(self, embedding: np.ndarray, k: int = 32) -> list[tuple[str, float]]:
        pass


class VideoRetriever(IRetriever):
    def __init__(self, embeddings: np.ndarray, labels: list[str], device: str = 'cpu'):
        self._labels = labels
        self._index = build_index(embeddings, device=device)
        self._device = device

    def retrieve(self, embedding: np.ndarray, k: int = 32) -> list[tuple[str, float]]:
        embedding = embedding.reshape(1, -1).astype(np.float32)
        if self._device != 'cpu':
            embedding = torch.tensor(embedding).to(self._device)

        faiss.normalize_L2(embedding)
        distances, indices = self._index.search(embedding, k)
        return [(self._labels[i], 1 - distances[0][j]) for j, i in enumerate(indices[0])]


class MultipleRetrievers(IRetriever):
    def __init__(self, retrievers: list[VideoRetriever]):
        self._retrievers = retrievers

    def retrieve(self, embedding: np.ndarray, k: int = 32) -> list[tuple[str, float]]:
        results = []
        for retriever in self._retrievers:
            results += retriever.retrieve(embedding, k=k)

        results.sort(key=lambda x: x[1], reverse=False)
        return results[:k]


def build_index(embeddings: np.ndarray, device: str = 'cpu') -> faiss.IndexFlatIP:
    index = faiss.IndexFlatIP(embeddings.shape[1])
    if device != 'cpu':
        index = faiss.index_cpu_to_all_gpus(index)

    embeddings = embeddings.astype(np.float32)
    for batch in chunked(embeddings, 10_000):  # setting limit fix malloc_error_break on macos
        batch = np.stack(batch)
        faiss.normalize_L2(batch)
        index.add(batch)  # noqa
    return index
