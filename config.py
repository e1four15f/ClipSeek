from pathlib import Path

# Dataset
DATASETS_PATH = Path("../data")
DATASETS = [
    # {
    #     "dataset": "MSRVTT",
    #     "version": "5sec",
    #     "modalities": ["video"],#, "audio"],
    # },
    {
        # maybe path here?
        "dataset": "MSVD",
        "version": "5sec",
        "modalities": ["video"],
    },
    {
        "dataset": "MSRVTT",
        "version": "all",
        "modalities": ["video", "audio"],
    },
    {
        "dataset": "COCO",
        "version": "val2017",
        "modalities": ["image"],
    },
    {
        "dataset": "COCO",
        "version": "test2017",
        "modalities": ["image"],
    },
]

# Models
USE_DUMMY_MODEL = False
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

# UI
DEBUG = False
N_RESULT_COLUMNS = 3
