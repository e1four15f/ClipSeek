import json
import os
from typing import TypedDict

import yaml

from src.entity.embedder import Modality


class _DatasetConfig(TypedDict):
    data_path: str
    dataset: str
    version: str
    modalities: list[Modality]


class Config:
    DEVELOPER_MODE: bool
    DEVICE: str
    TMP_DIR: str
    USE_DUMMY_MODEL: bool
    DATASETS: list[_DatasetConfig]
    MILVUS_URL: str
    MILVUS_DB_NAME: str
    BACKEND_URL: str
    CLIP_MODELS: dict[Modality, str]
    EMBEDDINGS_DIM: int
    INDEXES_ROOT: str

    @classmethod
    def load(cls, config_file: str) -> None:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Replace placeholders with environment variables
        for key, value in config.items():
            if isinstance(value, str):
                value = os.getenv(key, value)  # noqa: PLW2901
            setattr(cls, key, value)

    @classmethod
    def dump(cls) -> str:
        fields = {key: getattr(cls, key) for key in cls.__annotations__}
        return json.dumps(fields, indent=4)
