from functools import cache
from pathlib import Path

import numpy as np

import config as cfg
from backend.entity.embedder import IEmbedder, LanguageBindEmbedder, Modality, RandomEmbedder
from backend.entity.retriever import FaissMediaRetriever, MilvusMediaRetriever, MultipleRetrievers


@cache
def build_embedder() -> IEmbedder:
    if cfg.USE_DUMMY_MODEL:
        return RandomEmbedder(embeddings_dim=cfg.EMBEDDINGS_DIM)
    return LanguageBindEmbedder(models=cfg.CLIP_MODELS, device=cfg.DEVICE)


# @cache
# def build_retriever() -> MultipleRetrievers:
#     return MultipleRetrievers(
#         retrievers=[
#             get_retriever(
#                 dataset_path=DATASETS_PATH / d["dataset"],
#                 version=d["version"],
#                 modality=d["modality"],
#                 device=DEVICE,
#             )
#             for d in DATASETS
#         ]
#     )


@cache
def build_retriever() -> MultipleRetrievers:
    return MultipleRetrievers(
        retrievers=[
            _get_milvus_retriever(
                dataset_name=f'{d["dataset"]}_{d["version"]}',
                dataset_path=cfg.DATASETS_PATH / d["dataset"],
                version=d["version"],
                modalities=d["modalities"],
                device=cfg.DEVICE,
            )
            for d in cfg.DATASETS
        ]
    )


def _get_faiss_retriever(dataset_path: Path, version: str, modality: str, device: str) -> FaissMediaRetriever:
    index_path = dataset_path / "index" / version
    index_embeddings = np.load(index_path / f"{modality}_embeddings.npy")
    labels = [str(dataset_path / s) for s in (index_path / "labels.txt").open().read().splitlines()]
    return FaissMediaRetriever(embeddings=index_embeddings, labels=labels, device=device)


def _get_milvus_retriever(
    dataset_name: str, dataset_path: Path, version: str, modalities: tuple[str], device: str
) -> MilvusMediaRetriever:
    index_path = dataset_path / "index" / version
    index_embeddings = {modality: np.load(index_path / f"{modality}_embeddings.npy") for modality in modalities}
    if len(modalities) > 1:
        index_embeddings[Modality.HYBRID] = np.mean(list(index_embeddings.values()), axis=0)

    labels = [str(dataset_path / s) for s in (index_path / "labels.txt").open().read().splitlines()]
    return MilvusMediaRetriever(
        url=cfg.MILVUS_URL,
        database_name=cfg.MILVUS_DB_NAME,
        index_name=dataset_name,
        modality_embeddings=index_embeddings,  # noqa
        embeddings_dim=cfg.EMBEDDINGS_DIM,
        labels=labels,
        device=device,
    )
