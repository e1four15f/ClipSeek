from pathlib import Path

from src.embedder import Modality

# Dataset
DATASETS_PATH = Path("data")
DATASETS = [
    # {
    #     "dataset": "MSRVTT",
    #     "version": "5sec",
    #     "modalities": [Modality.VIDEO],#, Modality.AUDIO],
    # },
    {
        # maybe path here?
        "dataset": "MSVD",
        "version": "5sec",
        "modalities": [Modality.VIDEO],
    },
    {
        "dataset": "MSRVTT",
        "version": "all",
        "modalities": [Modality.VIDEO, Modality.AUDIO],
    },
    {
        "dataset": "COCO",
        "version": "val2017",
        "modalities": [Modality.IMAGE],
    },
    {
        "dataset": "COCO",
        "version": "test2017",
        "modalities": [Modality.IMAGE],
    },
]

# Models
USE_DUMMY_MODEL = True
CLIP_MODELS = {
    Modality.VIDEO: "LanguageBind_Video",
    Modality.AUDIO: "LanguageBind_Audio",
    Modality.IMAGE: "LanguageBind_Image",
}
EMBEDDINGS_DIM = 768

# System
MILVUS_URL = "http://localhost:19530"
MILVUS_DB_NAME = "MultimodalMediaSearch"
CANDIDATES_PER_PAGE = 32
DEVICE = "cpu"

# Backend
BACKEND_URL = "http://localhost:8500"

# UI
DEBUG = False
N_RESULT_COLUMNS = 3
