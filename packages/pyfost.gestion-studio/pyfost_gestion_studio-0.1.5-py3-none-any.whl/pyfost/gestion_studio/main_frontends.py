from .home import HomeFrontend
from .floors import FloorsFrontend
from .projects import ProjectsFrontend

from ._app import create_app, run_app

from .settings import PyFostSettings

settings = PyFostSettings()
runtime_settings = settings.runtime.frontends

app = create_app(
    title=runtime_settings.title,
    description=runtime_settings.description,
    version=runtime_settings.version,
    apps=(
        HomeFrontend(runtime_settings),
        FloorsFrontend(runtime_settings),
        ProjectsFrontend(runtime_settings),
    ),
)

if __name__ == "__main__":
    run_app(
        "pyfost.gestion_studio.main_frontends:app",
        host=runtime_settings.host,
        port=runtime_settings.port,
        reload=runtime_settings.reload,
    )
