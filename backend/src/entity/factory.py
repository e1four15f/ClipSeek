import logging
from functools import cache

from pymilvus import MilvusClient

from src.config import Config
from src.entity.embedder.base import EmbedderType, IEmbedder, Modality
from src.entity.embedder.language_bind import LanguageBindEmbedder
from src.entity.embedder.random import RandomEmbedder
from src.entity.retriever.retriever import MilvusSearchIteratorFactory
from src.entity.searcher.base import ISearcher
from src.entity.searcher.batch import BatchSearcher
from src.entity.storage.base import IStorage, StorageType
from src.entity.storage.milvus import MilvusStorage, create_milvus_connection
from src.types import Collection

logger = logging.getLogger(__name__)


@cache
def build_embedder(embedder_type: EmbedderType, device: str) -> IEmbedder:
    logger.info("Initializing %s embedder on device %s...", embedder_type, device)
    if embedder_type == EmbedderType.LANGUAGE_BIND:
        return LanguageBindEmbedder(device=device)
    if embedder_type == EmbedderType.RANDOM:
        return RandomEmbedder()
    raise NotImplementedError(f"Embedder type '{embedder_type}' is not implemented.")


@cache
def build_searcher() -> ISearcher:
    logger.info("Initializing Searcher...")
    # TODO move this to app.py?
    create_milvus_connection(
        url=Config.MILVUS_URL,
        database_name=Config.MILVUS_DB_NAME,
    )
    return BatchSearcher(
        iterator_factories={
            Collection(dataset=d["dataset"], version=d["version"]): _get_milvus_retriever(
                dataset=d["dataset"],
                version=d["version"],
                modalities=[Modality(m) for m in d["modalities"]],
            )
            for d in Config.DATASETS
        }
    )


@cache
def build_storage(storage_type: StorageType) -> IStorage:
    logger.info("Initializing %s Storage...", storage_type)
    if storage_type == StorageType.MILVUS:
        client = MilvusClient(uri=Config.MILVUS_URL, db_name=Config.MILVUS_DB_NAME)
        return MilvusStorage(client=client)
    if storage_type == StorageType.FAISS:
        pass  # TODO
    raise NotImplementedError(f"Storage type '{storage_type}' is not implemented.")


# TODO delete or support
# def _get_faiss_retriever(dataset: str, version: str, modalities: tuple[str], device: str
# ) -> FaissSearchIteratorFactory:
#     logger.info("Initializing FAISS retriever for dataset=%s version=%s...", dataset, version)
#     index_path = Path(Config.INDEXES_ROOT) / dataset / version
#     index_embeddings = {
#         modality: np.load(index_path / f"LanguageBind_{modality}_embeddings.npy") for modality in modalities
#     }  # TODO model hardcode
#     labels = (index_path / "labels.txt").open().read().splitlines()
#     return FaissSearchIteratorFactory(embeddings=index_embeddings, labels=labels, device=device)


def _get_milvus_retriever(
    dataset: str,
    version: str,
    modalities: list[Modality],
) -> MilvusSearchIteratorFactory:
    logger.info("Initializing Milvus retriever for dataset=%s version=%s...", dataset, version)
    return MilvusSearchIteratorFactory(
        collection_name=f"{dataset}__{version}",
        modalities=modalities,
    )
