# class FaissSearchIteratorFactory(ISearchIteratorFactory):
#     # TODO embedding as list[float], move building to index phase
#     def __init__(self, embeddings: np.ndarray, labels: list[str], device: str = "cpu"):
#         self._labels = labels
#         self._index = build_faiss_index(embeddings, device=device)
#         self._device = device
#
#     def retrieve(self, embedding: np.ndarray, modalities: list[Modality], k: int = 32) -> list[Candidate]:
#         embedding = embedding.reshape(1, -1).astype(np.float32)
#         if self._device != "cpu":
#             embedding = torch.tensor(embedding).to(self._device)
#
#         faiss.normalize_L2(embedding)
#         distances, indices = self._index.search(embedding, k)  # noqa
#         # TODO back compitability with milvus, add modality
#         return [(self._labels[i], 1 - distances[0][j]) for j, i in enumerate(indices[0])]
