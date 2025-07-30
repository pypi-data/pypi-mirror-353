from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from ...settings import PyFostSettings
from .admin import mount_admin
from .pages import mount_pages


async def startup(app: FastAPI):
    print("INFO:     Starting up Floors Frontend")


async def teardown(app: FastAPI):
    print("INFO:     Shutting down Floors Frontend...")


def mount(app: FastAPI, api_host: str, api_port: int):
    floors_app_frontend_router = APIRouter(prefix="/apps/floors")
    mount_pages(floors_app_frontend_router, api_host, api_port)
    mount_admin(floors_app_frontend_router, api_host, api_port)
    app.include_router(floors_app_frontend_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Floors Management Frontend",
    description="GUI for managing Facilities, Floors, Seats, Resources and Assigments.",
    version="0.1.0",
    lifespan=lifespan,
)

settings = PyFostSettings().apps.projects_frontend

mount(
    app,
    settings.api_host,
    settings.api_port,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pyfost.gestion_studio.floors.frontend.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
    )
