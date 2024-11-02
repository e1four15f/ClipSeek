import faiss
import numpy as np
from more_itertools import chunked


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
