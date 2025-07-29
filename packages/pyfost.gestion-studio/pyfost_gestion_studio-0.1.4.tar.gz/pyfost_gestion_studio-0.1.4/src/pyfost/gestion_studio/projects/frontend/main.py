from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from .admin import mount_admin
from .pages import mount_pages
from ...settings import PyFostSettings


async def startup(app: FastAPI):
    print("INFO:     Starting up Projects Frontend")


async def teardown(app: FastAPI):
    print("INFO:     Shutting down Projects Frontend...")


def mount(app: FastAPI, api_host: str, api_port: int):
    projects_app_frontend_router = APIRouter(prefix="/apps/projects")
    mount_pages(projects_app_frontend_router, api_host=api_host, api_port=api_port)
    mount_admin(projects_app_frontend_router, api_host=api_host, api_port=api_port)
    app.include_router(projects_app_frontend_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


settings = PyFostSettings().apps.projects_frontend

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan,
)


mount(app, settings.api_host, settings.api_port)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pyfost.gestion_studio.projects.frontend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
