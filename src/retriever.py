import numpy as np
import faiss
import torch


class VideoRetriever:
    def __init__(self, embeddings: np.ndarray, labels: list[str], device: str = 'cpu'):
        self._labels = labels
        self._device = device

        self._index = faiss.IndexFlatIP(embeddings.shape[1])
        if device != 'cpu':
            self._index = faiss.index_cpu_to_all_gpus(self._index)

        embeddings = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings)
        self._index.add(embeddings)

    def retrieve(self, embedding: np.ndarray, k: int = 32) -> list[tuple[str, float]]:
        embedding = embedding.reshape(1, -1).astype(np.float32)
        if self._device != 'cpu':
            embedding = torch.tensor(embedding).to(self._device).numpy()

        faiss.normalize_L2(embedding)
        distances, indices = self._index.search(embedding, k)
        return [(self._labels[i], 1 - distances[0][j]) for j, i in enumerate(indices[0])]
