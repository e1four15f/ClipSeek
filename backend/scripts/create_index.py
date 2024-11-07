import argparse
import json
from pathlib import Path

import numpy as np

from src.config import Config
from src.entity.embedder.base import EmbedderType, Modality
from src.entity.factory import build_storage
from src.entity.storage.base import StorageType
from src.entity.storage.milvus import build_milvus_collection


def main(
    indexes_root: Path,
    dataset_name: str,
    dataset_version: str,
    model_type: EmbedderType,
    storage_type: StorageType,
) -> None:
    Config.load(config_file="../config.yaml")

    index_path = Path(indexes_root) / dataset_name / dataset_version
    index_name = f"{dataset_name}__{dataset_version}"

    modality_embeddings: dict[Modality, np.ndarray] = {}
    embeddings_dim: int
    for file in Path(index_path).glob(f"{model_type}_*_embeddings.npy"):
        modality = file.stem.split("_")[1]  # Extract modality from the filename
        embeddings = np.load(file)
        modality_embeddings[Modality(modality)] = embeddings
        embeddings_dim = embeddings.shape[-1]

    if len(modality_embeddings) > 1:
        modality_embeddings[Modality.HYBRID] = np.mean(list(modality_embeddings.values()), axis=0)

    print("DATA: ", [x.shape for x in modality_embeddings.values()])
    with (index_path / "labels.jsonlines").open() as f:
        labels = [json.loads(line) for line in f]

    print("Building Milvus collections...")
    build_storage(storage_type)
    build_milvus_collection(
        index_name,
        modality_embeddings=modality_embeddings,
        embeddings_dim=embeddings_dim,  # noqa
        labels=labels,
    )
    print("Done!")


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Build an index from precomputed embeddings for a specific dataset version."
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
        "-m",
        type=EmbedderType,
        required=True,
        choices=[str(i.value) for i in EmbedderType],  # noqa
        default=EmbedderType.LANGUAGE_BIND,
        help="Embedder model",
    )

    args = parser.parse_args()
    main(
        indexes_root=Path("../indexes"),
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version,
        model_type=args.model,
        storage_type=StorageType.MILVUS,
    )


if __name__ == "__main__":
    run()
