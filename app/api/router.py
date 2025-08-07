from fastapi import APIRouter
from app.api.endpoints import PdfRoutes, PreprocessRoutes, SemanticSearchRoutes

def create_api_router_v1():
    api_router = APIRouter()

    try:
        routes = PdfRoutes()
        api_router.include_router(routes.router)

        preprocess_routes = PreprocessRoutes()
        api_router.include_router(preprocess_routes.router)

        semantic_search_routes = SemanticSearchRoutes()
        api_router.include_router(semantic_search_routes.router)

    except Exception as e:
        print(f"Error creating API router: {e}")
        raise e

    return api_router