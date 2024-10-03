import os
from typing import TypedDict

import yaml


class _DatasetConfig(TypedDict):
    data_path: str
    dataset: str
    version: str
    modalities: list[str]


class Config:
    CANDIDATES_PER_PAGE: int  # TODO order and remove
    DEVELOPER_MODE: bool
    DEVICE: str
    TMP_DIR: str
    USE_DUMMY_MODEL: bool
    DATASETS: list[_DatasetConfig]
    MILVUS_URL: str
    MILVUS_DB_NAME: str
    BACKEND_URL: str
    N_RESULT_COLUMNS: int
    CLIP_MODELS: dict[str, str]
    EMBEDDINGS_DIM: int
    INDEX_PATH: str

    @classmethod
    def load(cls, config_file: str) -> None:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Replace placeholders with environment variables
        for key, value in config.items():
            if isinstance(value, str):
                value = os.getenv(key, value)  # noqa: PLW2901
            setattr(cls, key, value)
