from pathlib import Path

from src.embedder import Modality

# Dataset
DATASETS_PATH = Path('data')
DATASETS = [
    {
        'dataset': 'MSRVTT',
        'version': 'videos/test',
        'modality': Modality.VIDEO,
    },
    {
        'dataset': 'MSRVTT',
        'version': 'videos/5sec',
        'modality': Modality.VIDEO,
    },
    {
        'dataset': 'MSRVTT',
        'version': 'videos/all',
        'modality': Modality.VIDEO,
    }
]

# Models
CLIP_MODELS = {Modality.VIDEO: 'LanguageBind_Video'}

# System
CANDIDATES_PER_PAGE = 32
DEVICE = 'cpu'
