# Dataset
from pathlib import Path

# TODO annoying ../../../
INDEX_PATH = Path("../data")
DATASETS = [
    # {
    #     "data_path": # path to raw data
    #     "dataset": # internal dataset name
    #     "version": # internal dataset version
    #     "modalities": # list of modalities to extract
    # },
    {
        "data_path": "../../data/MSVD/YouTubeClips",
        "dataset": "MSVD",
        "version": "all",
        "modalities": ["video"],
    },
    {
        "data_path": "../../data/MSRVTT/all",
        "dataset": "MSRVTT",
        "version": "train",
        "modalities": ["video", "audio"],
    },
    {
        "data_path": "../../data/MSRVTT/test",
        "dataset": "MSRVTT",
        "version": "test",
        "modalities": ["video"],
    },
    {
        "data_path": "../../data/COCO/val2017",
        "dataset": "COCO",
        "version": "val2017",
        "modalities": ["image"],
    },
    {
        "data_path": "../../data/COCO/test2017",
        "dataset": "COCO",
        "version": "test2017",
        "modalities": ["image"],
    },
]

# Models
USE_DUMMY_MODEL = True
CLIP_MODELS = {
    "video": "LanguageBind_Video",
    "audio": "LanguageBind_Audio",
    "image": "LanguageBind_Image",
}
EMBEDDINGS_DIM = 768


# System
MILVUS_URL = "http://localhost:19530"
MILVUS_DB_NAME = "MultimodalMediaSearch"
CANDIDATES_PER_PAGE = 32
DEVICE = "cpu"

# Backend
BACKEND_URL = "http://localhost:8500"
TMP_DIR = ".tmp"

# UI
DEBUG = False
N_RESULT_COLUMNS = 3
