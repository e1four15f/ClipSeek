import logging
from functools import cache
from pathlib import Path

import numpy as np
from pymilvus import MilvusClient

from src.config import Config
from src.entity.embedder import IEmbedder, LanguageBindEmbedder, Modality, RandomEmbedder
from src.entity.retriever.retriever import FaissSearchIteratorFactory, MilvusSearchIteratorFactory
from src.entity.retriever.utils import create_milvus_connection
from src.entity.searcher import BatchSearcher
from src.entity.storage import IStorage, MilvusStorage
from src.types import Collection

logger = logging.getLogger(__name__)


@cache
def build_embedder() -> IEmbedder:
    logger.info("Initializing Embedder...")
    if Config.USE_DUMMY_MODEL:
        return RandomEmbedder(embeddings_dim=Config.EMBEDDINGS_DIM)
    return LanguageBindEmbedder(models=Config.CLIP_MODELS, device=Config.DEVICE)


@cache
def build_searcher() -> BatchSearcher:
    logger.info("Initializing Searcher...")
    create_milvus_connection(
        url=Config.MILVUS_URL,
        database_name=Config.MILVUS_DB_NAME,
    )
    # TODO create collections here, not on Searcher initizlization
    return BatchSearcher(
        iterator_factories={
            Collection(dataset=d["dataset"], version=d["version"]): _get_milvus_retriever(
                dataset=d["dataset"],
                version=d["version"],
                modalities=d["modalities"],
            )
            for d in Config.DATASETS
        }
    )


@cache
def build_storage() -> IStorage:
    client = MilvusClient(uri=Config.MILVUS_URL, db_name=Config.MILVUS_DB_NAME)
    return MilvusStorage(client=client)


# TODO delete or support
def _get_faiss_retriever(dataset: str, version: str, modalities: tuple[str], device: str) -> FaissSearchIteratorFactory:
    logger.info("Initializing FAISS retriever for dataset=%s version=%s...", dataset, version)
    index_path = Path(Config.INDEX_PATH) / dataset / version
    index_embeddings = {
        modality: np.load(index_path / f"LanguageBind_{modality}_embeddings.npy") for modality in modalities
    }  # TODO model hardcode
    labels = (index_path / "labels.txt").open().read().splitlines()
    return FaissSearchIteratorFactory(embeddings=index_embeddings, labels=labels, device=device)


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
