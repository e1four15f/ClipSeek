from fastapi import FastAPI

import config as cfg
from backend.entity.factory import build_embedder, build_searcher
from backend.handler.info import InfoHandler
from backend.handler.resources import ResourcesHandler
from backend.handler.search.v1 import SearchHandler
from backend.server import AppServer, AppSettings


def get_app() -> FastAPI:
    settings = AppSettings()
    embedder = build_embedder()
    retriever = build_searcher()
    return AppServer(
        search_handler=SearchHandler(
            embedder=embedder,
            retriever=retriever,
            candidates_per_page=cfg.CANDIDATES_PER_PAGE,
        ),
        info_handler=InfoHandler(),
        resources_handler=ResourcesHandler(data_path=settings.data_path),
        settings=settings,
    ).create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_app(), host="localhost", port=8500)
