import numpy as np
import faiss
import torch
from more_itertools import chunked


class VideoRetriever:
    def __init__(self, embeddings: np.ndarray, labels: list[str], device: str = 'cpu'):
        self._labels = labels
        self._device = device
        self._index = faiss.IndexFlatIP(embeddings.shape[1])
        if device != 'cpu':
            self._index = faiss.index_cpu_to_all_gpus(self._index)

        embeddings = embeddings.astype(np.float32)
        for batch in chunked(embeddings, 10_000):  # setting limit fix malloc_error_break on macos
            batch = np.stack(batch)
            faiss.normalize_L2(batch)
            self._index.add(batch)

    def retrieve(self, embedding: np.ndarray, k: int = 32) -> list[tuple[str, float]]:
        embedding = embedding.reshape(1, -1).astype(np.float32)
        if self._device != 'cpu':
            embedding = torch.tensor(embedding).to(self._device)

        faiss.normalize_L2(embedding)
        distances, indices = self._index.search(embedding, k)
        return [(self._labels[i], 1 - distances[0][j]) for j, i in enumerate(indices[0])]
