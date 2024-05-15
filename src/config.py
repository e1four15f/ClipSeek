from pathlib import Path

from src.embedder import Modality

# Dataset
DATASET_PATH = Path('data')
DATASET = 'MSRVTT'
DATASET_TYPE = 'all'

# Models
CLIP_MODELS = {Modality.VIDEO: 'LanguageBind_Video'}

# System
CANDIDATES_PER_PAGE = 32
DEVICE = 'cpu'
