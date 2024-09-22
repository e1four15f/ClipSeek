import json
import logging
from functools import cache

import numpy as np

import config as cfg
from src.entity.embedder import IEmbedder, LanguageBindEmbedder, Modality, RandomEmbedder
from src.entity.retriever.retriever import FaissSearchIteratorFactory, MilvusSearchIteratorFactory
from src.entity.retriever.utils import create_milvus_connection
from src.entity.searcher import BatchSearcher

logger = logging.getLogger(__name__)


@cache
def build_embedder() -> IEmbedder:
    logger.info("Initializing Embedder...")
    if cfg.USE_DUMMY_MODEL:
        return RandomEmbedder(embeddings_dim=cfg.EMBEDDINGS_DIM)
    return LanguageBindEmbedder(models=cfg.CLIP_MODELS, device=cfg.DEVICE)


@cache
def build_searcher() -> BatchSearcher:
    logger.info("Initializing Searcher...")
    create_milvus_connection(
        url=cfg.MILVUS_URL,
        database_name=cfg.MILVUS_DB_NAME,
    )
    # TODO create collections here, not on Searcher initizlization
    return BatchSearcher(
        iterator_factories={
            (d["dataset"], d["version"]): _get_milvus_retriever(
                dataset=d["dataset"],
                version=d["version"],
                modalities=d["modalities"],
                device=cfg.DEVICE,
            )
            for d in cfg.DATASETS
        }
    )


# TODO delete or support
def _get_faiss_retriever(dataset: str, version: str, modalities: tuple[str], device: str) -> FaissSearchIteratorFactory:
    logger.info("Initializing FAISS retriever for dataset=%s version=%s...", dataset, version)
    index_path = cfg.INDEX_PATH / dataset / version
    index_embeddings = {
        modality: np.load(index_path / f"LanguageBind_{modality}_embeddings.npy") for modality in modalities
    }  # TODO model hardcode
    labels = (index_path / "labels.txt").open().read().splitlines()
    return FaissSearchIteratorFactory(embeddings=index_embeddings, labels=labels, device=device)


def _get_milvus_retriever(
    dataset: str,
    version: str,
    modalities: tuple[str],
    device: str,  # noqa: ARG001
) -> MilvusSearchIteratorFactory:
    logger.info("Initializing Milvus retriever for dataset=%s version=%s...", dataset, version)
    index_path = cfg.INDEX_PATH / dataset / version
    index_embeddings = {
        modality: np.load(index_path / f"LanguageBind_{modality}_embeddings.npy") for modality in modalities
    }  # TODO model hardcode
    if len(modalities) > 1:
        index_embeddings[Modality.HYBRID] = np.mean(list(index_embeddings.values()), axis=0)

    with open(index_path / "labels.jsonlines") as f:
        labels = [json.loads(line) for line in f]

    return MilvusSearchIteratorFactory(
        index_name=f"{dataset}__{version}",
        modality_embeddings=index_embeddings,  # noqa
        embeddings_dim=cfg.EMBEDDINGS_DIM,
        labels=labels,
    )
