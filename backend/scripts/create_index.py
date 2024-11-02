import argparse
import json
from pathlib import Path

import numpy as np

from src.config import Config
from src.entity.embedder.base import EmbedderType, Modality
from src.entity.storage.base import StorageType
from src.entity.storage.milvus import build_milvus_collection, create_milvus_connection


def main(
    indexes_root: Path,
    dataset_name: str,
    dataset_version: str,
    model: EmbedderType,
    storage: StorageType,
) -> None:
    index_path = Path(indexes_root) / dataset_name / dataset_version
    index_name = f"{dataset_name}__{dataset_version}"

    modality_embeddings = {}
    embeddings_dim = None
    for file in Path(index_path).glob(f"{model}_*_embeddings.npy"):
        modality = file.stem.split("_")[1]  # Extract modality from the filename
        embeddings = np.load(file)
        modality_embeddings[modality] = embeddings
        embeddings_dim = embeddings.shape[-1]

    if len(modality_embeddings) > 1:
        modality_embeddings[Modality.HYBRID] = np.mean(list(modality_embeddings.values()), axis=0)

    print("DATA: ", [x.shape for x in modality_embeddings.values()])
    with (index_path / "labels.jsonlines").open() as f:
        labels = [json.loads(line) for line in f]

    # TODO here would be an if for FAISS index
    create_milvus_connection(
        url=Config.MILVUS_URL,  # TODO move to args
        database_name=Config.MILVUS_DB_NAME,  # TODO hardcode
    )
    # TODO ability to add aknn index or index params. Put them into args as json
    build_milvus_collection(
        index_name, modality_embeddings=modality_embeddings, embeddings_dim=embeddings_dim, labels=labels
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "--indexes-root",
        type=Path,
        default="../indexes",
        help="Path to the root directory where computed indexes will be stored.",
    )
    parser.add_argument(
        "--dataset-name", "--name", "-n", type=str, required=True, help="Name of the dataset (e.g., 'VideoDataset')."
    )
    parser.add_argument(
        "--dataset-version",
        "--version",
        "-v",
        type=str,
        required=True,
        help="Version of the dataset (e.g., 'v1.0', '5s').",
    )
    parser.add_argument(
        "--model",
        type=EmbedderType,
        required=True,
        choices=list(EmbedderType),  # noqa
        default=EmbedderType.LANGUAGE_BIND,
        help="Embedder model",
    )
    parser.add_argument(
        "--storage",
        type=StorageType,
        required=True,
        choices=list(StorageType),  # noqa
        default=StorageType.MILVUS,
        help="Storage type",
    )

    args = parser.parse_args()
    main(
        indexes_root=Path(args.indexes_root),
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version,
        model=args.model,
        storage=args.storage,
    )
