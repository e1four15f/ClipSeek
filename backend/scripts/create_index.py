import argparse
import json
from pathlib import Path

import numpy as np

from src.config import Config
from src.entity.embedder import Modality
from src.entity.retriever.utils import build_milvus_collection, create_milvus_connection


def main(indexes_root: Path, dataset_name: str, dataset_version: str, modalities: list[Modality]) -> None:
    config_file = "../config.yaml"
    print(f"Loading config file: {config_file}")
    Config.load(config_file=config_file)

    index_path = Path(indexes_root) / dataset_name / dataset_version
    index_name = f"{dataset_name}__{dataset_version}"

    print("Creating milvus connection...")
    create_milvus_connection(
        url=Config.MILVUS_URL,
        database_name=Config.MILVUS_DB_NAME,
    )
    modality_embeddings = {
        modality: np.load(index_path / f"LanguageBind_{modality}_embeddings.npy") for modality in modalities
    }  # TODO model hardcode
    if len(modalities) > 1:
        modality_embeddings[Modality.HYBRID] = np.mean(list(modality_embeddings.values()), axis=0)

    print("DATA: ", [x.shape for x in modality_embeddings.values()])
    embeddings_dim = 768
    with (index_path / "labels.jsonlines").open() as f:
        labels = [json.loads(line) for line in f]

    build_milvus_collection(
        index_name, modality_embeddings=modality_embeddings, embeddings_dim=embeddings_dim, labels=labels
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--indexes-root", type=Path, default="../indexes", help="Path to the indexes root directory")
    parser.add_argument(
        "--dataset-name",
        "--name",
        "-n",
        type=str,
        required=True,
        help="",
    )
    parser.add_argument(
        "--dataset-version",
        "--version",
        "-v",
        type=str,
        required=True,
        help="",
    )
    parser.add_argument(
        "--modality",
        "-m",
        type=Modality,
        choices=[Modality.VIDEO, Modality.IMAGE, Modality.AUDIO],
        default=Modality.VIDEO,
        help="",
    )

    args = parser.parse_args()
    main(
        indexes_root=Path(args.indexes_root),
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version,
        modalities=[args.modality],
    )
