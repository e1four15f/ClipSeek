from collections.abc import Iterator

from pymilvus import Collection

from src.entity.embedder.base import Modality
from src.entity.retriever.base import IRetriever
from src.types import Candidate


class MilvusRetriever(IRetriever):
    def __init__(
        self,
        collection_name: str,
        modalities: list[Modality],
    ):
        self._collection = Collection(collection_name)
        self._collection.load()
        self._available_modalities = set(modalities)

    def create_iterator(
        self, embedding: list[float], modalities: list[Modality], batch_size: int
    ) -> Iterator[list[Candidate]]:
        request_modalities = list(set(modalities) & self._available_modalities)
        if not request_modalities:
            raise ValueError(f"Can not create iterator for selected modalities {modalities}.")

        search_iterator = self._collection.search_iterator(
            [embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE"},
            batch_size=batch_size,
            limit=2**10,
            partition_names=request_modalities,
            output_fields=["id", "path", "modality", "start", "end"],
        )

        def _iterator() -> Iterator[list[Candidate]]:
            try:
                while True:
                    hits = search_iterator.next()
                    if not hits:
                        break
                    yield [
                        Candidate(
                            id=hit.id,
                            path=hit.path,
                            score=1 - hit.distance,
                            modality=Modality(hit.modality),
                            span=(round(hit.start, 2), round(hit.end, 2)),
                        )
                        for hit in hits
                    ]
            finally:
                search_iterator.close()

        return _iterator()
