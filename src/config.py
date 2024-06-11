from pathlib import Path

from src.embedder import Modality

# Dataset
DATASETS_PATH = Path('data')
DATASETS = [
    {
        'dataset': 'MSRVTT',
        'version': '5sec',
        'modality': Modality.VIDEO,
    },
    {
        'dataset': 'MSVD',
        'version': '5sec',
        'modality': Modality.VIDEO,
    },
    # {
    #     'dataset': 'MSRVTT',
    #     'version': 'all',
    #     'modality': Modality.VIDEO,
    # },
    {
        'dataset': 'COCO',
        'version': 'val2017',
        'modality': Modality.IMAGE,
    },
    {
        'dataset': 'COCO',
        'version': 'test2017',
        'modality': Modality.IMAGE,
    }
]

# Models
CLIP_MODELS = {
    Modality.VIDEO: "LanguageBind_Video",
    # Modality.AUDIO: "LanguageBind_Audio",
    Modality.IMAGE: "LanguageBind_Image",
}

# System
CANDIDATES_PER_PAGE = 32
DEVICE = 'cpu'
DEBUG = False
