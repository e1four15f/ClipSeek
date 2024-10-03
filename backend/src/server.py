import logging
import os
import shutil
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.datastructures import Default
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from config import TMP_DIR
from src.handler.info import IInfoHandler
from src.handler.resources import IResourcesHandler
from src.handler.search.v1 import ISearchHandler

logger = logging.getLogger(__name__)


class AppServer:
    _ORIGINS = ["*"]

    def __init__(
        self,
        search_handler: ISearchHandler,
        info_handler: IInfoHandler,
        resources_handler: IResourcesHandler,
    ) -> None:
        self._search_handler = search_handler
        self._resources_handler = resources_handler
        self._info_handler = info_handler

    def create_application(self) -> FastAPI:
        logger.info("Creating application...")
        app = FastAPI(title="ClipSeek Backend", lifespan=_lifespan)
        app.add_middleware(
            CORSMiddleware,  # noqa
            allow_origins=self._ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        router = APIRouter(default_response_class=Default(ORJSONResponse))
        router.add_api_route(
            "/api/v1/search/by_text",
            self._search_handler.search_by_text,
            methods=["POST"],
            tags=["Search"],
        )
        router.add_api_route(
            "/api/v1/search/by_file",
            self._search_handler.search_by_file,
            methods=["POST"],
            tags=["Search"],
        )
        router.add_api_route(
            "/api/v1/search/by_reference",
            self._search_handler.search_by_reference,
            methods=["POST"],
            tags=["Search"],
        )
        router.add_api_route(
            "/api/v1/search/continue",
            self._search_handler.continue_search,
            methods=["POST"],
            tags=["Search"],
        )
        router.add_api_route(
            "/indexes/info",
            self._info_handler.get_indexes_info,
            methods=["GET"],
            tags=["Indexes"],
        )
        router.add_api_route(
            "/resources/raw/{dataset:str}/{version:str}/{file_path:path}",
            self._resources_handler.get_raw,
            methods=["GET"],
            tags=["File-Proxy"],
        )
        router.add_api_route(
            "/resources/clip/{dataset:str}/{version:str}/{file_path:path}",
            self._resources_handler.get_clip,
            methods=["GET"],
            tags=["File-Proxy"],
        )
        router.add_api_route(
            "/resources/thumbnail/{dataset:str}/{version:str}/{file_path:path}",
            self._resources_handler.get_thumbnail,
            methods=["GET"],
            tags=["File-Proxy"],
        )
        app.include_router(router)
        logger.info("Starting app...")
        return app


@asynccontextmanager
async def _lifespan(app: FastAPI):  # noqa
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    yield
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
