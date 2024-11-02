from typing import Union

import torch

from src.entity.embedder.base import IEmbedder, Modality


class RandomEmbedder(IEmbedder):
    def __init__(self, embeddings_dim: int):
        self._embeddings_dim = embeddings_dim

    def embed(self, data: Union[str, list[str], torch.Tensor], modality: Modality) -> torch.Tensor:  # noqa
        if isinstance(data, str):
            # for single input data return embeddings without batch_size dim
            return torch.rand(self._embeddings_dim)
        return torch.rand(len(data), self._embeddings_dim)
