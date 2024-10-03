import logging

import transformers
from fastapi import FastAPI

from src.config import Config
from src.entity.factory import build_embedder, build_searcher, build_storage
from src.handler.info import InfoHandler
from src.handler.resources import ResourcesHandler
from src.handler.search.v1 import SearchHandler
from src.server import AppServer

transformers.logging.set_verbosity_info()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    Config.load(config_file="../config.yaml")
    logger.info("Config: %s", Config.dump())

    embedder = build_embedder()
    searcher = build_searcher()
    storage = build_storage()

    return AppServer(
        search_handler=SearchHandler(
            embedder=embedder,
            storage=storage,
            searcher=searcher,
            candidates_per_page=Config.CANDIDATES_PER_PAGE,
        ),
        info_handler=InfoHandler(),
        resources_handler=ResourcesHandler(
            dataset_paths={(d["dataset"], d["version"]): d["data_path"] for d in Config.DATASETS}
        ),
    ).create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_app(), host="localhost", port=8500)
