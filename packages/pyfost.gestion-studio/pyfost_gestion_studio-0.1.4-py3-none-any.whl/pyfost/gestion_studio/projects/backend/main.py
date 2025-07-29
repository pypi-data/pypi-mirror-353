"""
Use this to spawn a standalone Projects service.

"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .routers import users, projects, tasks

from ...settings import PyFostSettings


async def startup(app: FastAPI):
    print("INFO:     Starting up Projects API and creating database tables...")
    create_db_and_tables()


async def teardown(app: FastAPI):
    print("INFO:     Shutting down Projects API...")


def mount(app: FastAPI):
    app.include_router(projects.router, prefix="/api/projects")
    app.include_router(users.router, prefix="/api/projects")
    app.include_router(tasks.router, prefix="/api/projects")


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


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Projects API!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pyfost.gestion_studio.projects.backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
