from typing import Any, Optional

import torch

from LanguageBind.languagebind import LanguageBind, transform_dict, to_device
from LanguageBind.languagebind.image.tokenization_image import LanguageBindImageTokenizer


class LanguageBindEmbedder:
    def __init__(
        self,
        models: Optional[dict[str, str]] = None,
        tokenizer_path: str = 'LanguageBind/LanguageBind_Image',
        device: str = 'cpu'
    ):
        self._device = torch.device(device)
        clip_type = models or {
            'video': 'LanguageBind_Video',
            'audio': 'LanguageBind_Audio',
            'thermal': 'LanguageBind_Thermal',
            'image': 'LanguageBind_Image',
            'depth': 'LanguageBind_Depth',
        }
        self._model = LanguageBind(clip_type=clip_type)
        self._model.to(device)
        self._model.eval()
        self._tokenizer = LanguageBindImageTokenizer.from_pretrained(
            tokenizer_path,
        )
        self._modality_transform = {c: transform_dict[c](self._model.modality_config[c]) for c in clip_type.keys()}

    def embed_text(self, text: str) -> torch.Tensor:
        inputs = {
            # 'image': to_device(self._modality_transform['image'](image), self._device),
            # 'video': to_device(self._modality_transform['video'](video), self._device),
            # 'audio': to_device(self._modality_transform['audio'](audio), self._device),
            # 'depth': to_device(self._modality_transform['depth'](depth), self._device),
            # 'thermal': to_device(self._modality_transform['thermal'](thermal), self._device),
            'language': to_device(
                self._tokenizer(text, max_length=77, padding='max_length', truncation=True, return_tensors='pt'),
                self._device
            )
        }
        return self.embed(inputs)['language'][0]

    def embed(self, inputs: dict[str, Any]) -> dict[str, torch.Tensor]:
        with torch.no_grad():
            embeddings = self._model(inputs)
        return embeddings
