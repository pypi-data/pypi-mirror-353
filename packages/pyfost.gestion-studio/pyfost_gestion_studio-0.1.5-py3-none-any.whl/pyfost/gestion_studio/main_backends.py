from .floors import FloorsBackend
from .projects import ProjectsBackend

from ._app import create_app, run_app

from .settings import PyFostSettings

settings = PyFostSettings()
runtime_settings = settings.runtime.backends

app = create_app(
    title=runtime_settings.title,
    description=runtime_settings.description,
    version=runtime_settings.version,
    apps=(
        FloorsBackend(runtime_settings),
        ProjectsBackend(runtime_settings),
    ),
)

if __name__ == "__main__":
    run_app(
        "pyfost.gestion_studio.main_backends:app",
        host=runtime_settings.host,
        port=runtime_settings.port,
        reload=runtime_settings.reload,
    )
