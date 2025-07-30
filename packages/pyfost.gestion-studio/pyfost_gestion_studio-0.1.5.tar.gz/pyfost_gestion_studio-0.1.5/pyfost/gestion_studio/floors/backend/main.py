"""
Use this to spawn a standalone Projects service.

"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .routers import assignations, resources, seats, tasks, io
from ...settings import PyFostSettings


async def startup(app: FastAPI):
    print("INFO:     Starting up Floors API and creating database tables...")
    create_db_and_tables()


async def teardown(app: FastAPI):
    print("INFO:     Shutting down Floors API...")


def mount(app: FastAPI):
    app.include_router(tasks.router, prefix="/api/floors")
    app.include_router(assignations.router, prefix="/api/floors")
    app.include_router(resources.router, prefix="/api/floors")
    app.include_router(seats.router, prefix="/api/floors")
    app.include_router(io.router, prefix="/api/io")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    yield
    await teardown(app)


settings = PyFostSettings().apps.projects_backend

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan,
)

mount(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pyfost.gestion_studio.floors.backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
