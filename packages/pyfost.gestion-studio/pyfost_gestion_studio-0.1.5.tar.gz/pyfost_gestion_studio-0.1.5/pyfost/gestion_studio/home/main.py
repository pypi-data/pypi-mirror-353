from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from nicegui import ui

from ..settings import PyFostSettings

from .page import home_page
from .home_config_page import home_config_page


async def startup(app: FastAPI):
    print("INFO:     Starting up Home Frontend")


async def teardown(app: FastAPI):
    print("INFO:     Shutting down Home Frontend...")


def mount(app: FastAPI, api_host: str, api_port: int):
    ui.page("/")(home_page)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Home",
    description="PyFost Home",
    version="0.1.0",
    lifespan=lifespan,
)

settings = PyFostSettings().apps.home_frontend

mount(
    app,
    settings.api_host,
    settings.api_port,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pyfost.gestion_studio.home.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
    )
