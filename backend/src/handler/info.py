from abc import ABC, abstractmethod

from pydantic import BaseModel, RootModel
from pymilvus import Collection
from pymilvus.orm import utility


class IndexInfo(BaseModel):
    dataset: str
    version: str
    count: int


IndexesInfoResponse = RootModel[list[IndexInfo]]


class IInfoHandler(ABC):
    @abstractmethod
    async def get_indexes_info(self) -> IndexesInfoResponse:
        pass


class InfoHandler(IInfoHandler):
    async def get_indexes_info(self) -> IndexesInfoResponse:
        collections = utility.list_collections()
        infos = []
        for collection_name in collections:
            collection = Collection(collection_name)
            dataset, version = collection_name.split("__")
            infos.append(IndexInfo(dataset=dataset, version=version, count=collection.num_entities))
        return IndexesInfoResponse(infos)
