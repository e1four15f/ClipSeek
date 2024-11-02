import logging

import transformers
from fastapi import FastAPI

from src.config import Config
from src.entity.factory import build_embedder, build_searcher, build_storage
from src.handler.info import InfoHandler
from src.handler.resources import ResourcesHandler
from src.handler.search.v1 import SearchHandler
from src.server import AppServer
from src.types import Collection

transformers.logging.set_verbosity_info()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    Config.load(config_file="../config.yaml")
    logger.info("Config: %s", Config.dump())

    embedder = build_embedder(Config.EMBEDDER_TYPE, device=Config.DEVICE)
    searcher = build_searcher()
    storage = build_storage(Config.STORAGE_TYPE)

    dataset_paths = {Collection(dataset=d["dataset"], version=d["version"]): d["data_path"] for d in Config.DATASETS}

    return AppServer(
        search_handler=SearchHandler(
            embedder=embedder,
            storage=storage,
            searcher=searcher,
        ),
        info_handler=InfoHandler(storage=storage, available_collections=list(dataset_paths.keys())),
        resources_handler=ResourcesHandler(dataset_paths=dataset_paths),
    ).create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_app(), host="localhost", port=8500)
