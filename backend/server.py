from fastapi import APIRouter, FastAPI
from fastapi.datastructures import Default
from fastapi.responses import ORJSONResponse
from pydantic.v1 import BaseSettings

from backend.handler.info import IInfoHandler
from backend.handler.resources import IResourcesHandler
from backend.handler.search.v1 import ISearchHandler, SearchResponse


class AppSettings(BaseSettings):
    data_path: str = "/Users/v.karmazin/repos/diploma/"  # TODO data and paths


class AppServer:
    def __init__(
        self,
        search_handler: ISearchHandler,
        info_handler: IInfoHandler,
        resources_handler: IResourcesHandler,
        settings: AppSettings,
    ) -> None:
        self._search_handler = search_handler
        self._resources_handler = resources_handler
        self._info_handler = info_handler
        self._settings = settings

    def create_application(self) -> FastAPI:
        app = FastAPI()
        router = APIRouter(default_response_class=Default(ORJSONResponse))
        router.add_api_route(
            "/api/v1/search/by_text",
            self._search_handler.search_by_text,
            methods=["POST"],
            tags=["Search"],
            response_model=SearchResponse,
        )
        router.add_api_route(
            "/api/v1/search/continue",
            self._search_handler.continue_search,
            methods=["POST"],
            tags=["Search"],
            response_model=SearchResponse,
        )
        router.add_api_route(
            "/indexes/info",
            self._info_handler.get_indexes_info,
            methods=["GET"],
            tags=["Indexes"],
        )
        router.add_api_route(
            "/resources/{file_path:path}",
            self._resources_handler.get_resource,
            methods=["GET"],
            tags=["File-Proxy"],
        )
        app.include_router(router)
        return app
