from enum import Enum
from functools import lru_cache
from typing import Any, Optional, Union

import torch

from LanguageBind.languagebind import LanguageBind, to_device, transform_dict
from LanguageBind.languagebind.image.tokenization_image import LanguageBindImageTokenizer


class Modality(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    THERMAL = "thermal"
    IMAGE = "image"
    DEPTH = "depth"
    TEXT = "language"


class LanguageBindEmbedder:
    def __init__(
        self,
        models: Optional[dict[Modality, str]] = None,
        tokenizer_path: str = "LanguageBind/LanguageBind_Image",
        device: str = "cpu",
    ):
        self._device = torch.device(device)
        clip_type = models or {
            Modality.VIDEO: "LanguageBind_Video",
            Modality.AUDIO: "LanguageBind_Audio",
            Modality.THERMAL: "LanguageBind_Thermal",
            Modality.IMAGE: "LanguageBind_Image",
            Modality.DEPTH: "LanguageBind_Depth",
        }
        self._model = LanguageBind(clip_type=clip_type)
        self._model.to(device)
        self._model.eval()
        self._tokenizer = LanguageBindImageTokenizer.from_pretrained(
            tokenizer_path,
        )
        self._modality_transform = {
            c: transform_dict[c](self._model.modality_config[c]) for c in clip_type
        }
        self._modality_transform[Modality.TEXT] = lambda text: self._tokenizer(
            text, max_length=77, padding="max_length", truncation=True, return_tensors="pt"
        )

    @lru_cache  # noqa
    def embed(self, data: Union[str, list[str], torch.Tensor], modality: Modality) -> torch.Tensor:
        inputs = {modality: data}
        if not isinstance(data, torch.Tensor):
            inputs = self._preprocess_inputs(inputs)

        with torch.no_grad():
            outputs = self._model(inputs)

        embeddings = outputs[modality]
        if isinstance(data, str):
            # for single input data return embeddings without batch_size dim
            return embeddings[0]
        return embeddings

    def _preprocess_inputs(self, inputs: dict[Modality, Any]) -> dict[Modality, torch.Tensor]:
        for modality, data in inputs.items():
            inputs[modality] = to_device(self._modality_transform[modality](data), self._device)
        return inputs
