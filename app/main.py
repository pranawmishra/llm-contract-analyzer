from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import create_api_router_v1


@asynccontextmanager
async def lifespan(app: FastAPI):

    api_router_v1 = create_api_router_v1()

    app.include_router(api_router_v1)

    yield

    print("Shutting down...")


def create_app():
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    return app

app = create_app()