import os

from .home import HomeFrontend
from .floors import FloorsBackend, FloorsFrontend
from .projects import ProjectsBackend, ProjectsFrontend

from ._app import create_app, run_app

from .settings import PyFostSettings


settings = PyFostSettings()
runtime_settings = settings.runtime.all

app = create_app(
    title=runtime_settings.title,
    description=runtime_settings.description,
    version=runtime_settings.version,
    apps=(
        HomeFrontend(settings=runtime_settings),
        FloorsBackend(settings=runtime_settings),
        FloorsFrontend(settings=runtime_settings),
        ProjectsBackend(settings=runtime_settings),
        ProjectsFrontend(settings=runtime_settings),
    ),
)

if __name__ == "__main__":
    run_app(
        "pyfost.gestion_studio.main_all:app",
        host=runtime_settings.host,
        port=runtime_settings.port,
        reload=runtime_settings.reload,
    )
