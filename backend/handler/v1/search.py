from backend.entity.embedder import IEmbedder, Modality
from backend.entity.retriever import MultipleRetrievers
from backend.handler.base import ISearchHandler, SearchRequest, SearchResponse, SearchResult


class SearchHandler(ISearchHandler):
    def __init__(
        self,
        embedder: IEmbedder,
        retriever: MultipleRetrievers,
        candidates_per_page: int,
    ) -> None:
        self._embedder = embedder
        self._retriever = retriever
        self._candidates_per_page = candidates_per_page

    def search_by_text(self, request: SearchRequest) -> SearchResponse:
        query_embedding = self._embedder.embed(request.query, modality=Modality.TEXT)
        candidates = self._retriever.retrieve(
            query_embedding.detach().numpy(),
            ignore_retrievers=request.datasets,
            modalities=request.modalities,
            k=self._candidates_per_page,
        )
        return SearchResponse(
            data=[
                SearchResult(
                    dataset="kek",  # TODO
                    version="v1",
                    path=path,
                    score=score,
                    modality=modality,
                )
                for path, score, modality in candidates
            ],
            hits=len(candidates),
        )
