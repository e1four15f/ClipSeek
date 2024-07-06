from fastapi import FastAPI

import config as cfg
from backend.factory import build_embedder, build_retriever
from backend.handler.resources import ResourcesHandler
from backend.handler.v1.search import SearchHandler
from backend.server import AppServer, AppSettings


def get_app() -> FastAPI:
    settings = AppSettings()
    embedder = build_embedder()
    retriever = build_retriever()
    return AppServer(
        search_handler=SearchHandler(
            embedder=embedder,
            retriever=retriever,
            candidates_per_page=cfg.CANDIDATES_PER_PAGE,
        ),
        resources_handler=ResourcesHandler(data_path=settings.data_path),
        settings=settings,
    ).create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_app(), host="localhost", port=8500)
