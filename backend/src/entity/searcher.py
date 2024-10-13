import uuid
from collections.abc import Generator, Iterator

from src.entity.embedder import Modality
from src.entity.retriever.retriever import ISearchIteratorFactory
from src.types import Candidate, CandidateWithCollection, Collection


class BatchSearcher:
    def __init__(self, iterator_factories: dict[Collection, ISearchIteratorFactory]):
        self._iterator_factories = iterator_factories
        self._sessions = {}  # TODO TTL CACHE because it increates over time?

    def search(
        self,
        embedding: list[float],
        collections: list[Collection],
        modalities: list[Modality],
        batch_size: int = 32,
    ) -> tuple[list[CandidateWithCollection], str]:
        session_id = str(uuid.uuid4())
        iterators = {}
        for collection in collections:
            try:
                iterators[collection] = self._iterator_factories[collection].create_iterator(
                    embedding=embedding,
                    modalities=modalities,
                    batch_size=batch_size,
                )
            except ValueError:
                continue
        search_generator = self._create_search_generator(iterators, batch_size=batch_size)
        self._sessions[session_id] = search_generator
        return next(search_generator), session_id

    def next(self, session_id: str) -> list[CandidateWithCollection]:
        try:
            return next(self._sessions[session_id])
        except StopIteration as e:
            del self._sessions[session_id]
            raise e

    def _create_search_generator(
        self, iterators: dict[Collection, Iterator[list[Candidate]]], batch_size: int
    ) -> Generator[list[CandidateWithCollection]]:
        def _search_generator() -> Generator[list[CandidateWithCollection]]:
            buffer = []
            while iterators:
                for collection, iterator in list(iterators.items()):
                    try:
                        candidates = next(iterator)
                        if candidates:
                            for candidate in candidates:
                                buffer.append(
                                    CandidateWithCollection(
                                        id=candidate.id,
                                        path=candidate.path,
                                        score=candidate.score,
                                        modality=candidate.modality,
                                        span=candidate.span,
                                        dataset=collection.dataset,
                                        version=collection.version,
                                    )
                                )
                    except StopIteration:
                        del iterators[collection]
                if buffer:
                    buffer.sort(key=lambda x: x.score, reverse=False)
                    yield buffer[:batch_size]
                    buffer = buffer[batch_size:]
                else:
                    break

        return _search_generator()
