from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

import torch


class Modality(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "language"
    # Combined modalities
    HYBRID = "hybrid"

    @classmethod
    def get_order(cls) -> list["Modality"]:
        return [cls.HYBRID, cls.VIDEO, cls.IMAGE, cls.AUDIO, cls.TEXT]


class EmbedderType(str, Enum):
    LANGUAGE_BIND = "LanguageBind"
    RANDOM = "Random"


class IEmbedder(ABC):
    @abstractmethod
    def embed(self, data: Union[str, list[str], torch.Tensor], modality: Modality) -> torch.Tensor:
        pass
