from abc import ABC, abstractmethod

from pydantic import BaseModel, RootModel

from src.entity.embedder import Modality
from src.entity.storage import IStorage
from src.types import Collection


class IndexInfo(BaseModel):
    dataset: str
    version: str
    count: int
    modalities: list[Modality]


IndexesInfoResponse = RootModel[list[IndexInfo]]


class IInfoHandler(ABC):
    @abstractmethod
    async def get_indexes_info(self) -> IndexesInfoResponse:
        pass


class InfoHandler(IInfoHandler):
    def __init__(self, storage: IStorage, available_collections: list[Collection]):
        self._storage = storage
        self._available_collections = available_collections

    async def get_indexes_info(self) -> IndexesInfoResponse:
        collections = self._storage.get_collections()
        infos = []
        modalities_order = Modality.get_order()
        for collection in collections:
            dataset, version = collection.name.split("__")
            if (dataset, version) not in self._available_collections:
                continue

            modalities = sorted(
                collection.partitions,
                key=lambda x: modalities_order.index(Modality(x)),
            )
            infos.append(
                IndexInfo(dataset=dataset, version=version, count=collection.row_count, modalities=modalities)
            )
        return IndexesInfoResponse(infos)
