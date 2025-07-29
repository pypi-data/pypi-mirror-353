from .._app import AppBackend, AppFrontend, FastAPI

from .backend import main as projects_backend_main

from .frontend import main as projects_frontend_main


class ProjectsBackend(AppBackend):
    async def startup(self, app: FastAPI):
        await projects_backend_main.startup(app)

    async def teardown(self, app: FastAPI):
        await projects_backend_main.teardown(app)

    def mount(self, app: FastAPI):
        projects_backend_main.mount(app)


class ProjectsFrontend(AppFrontend):
    async def startup(self, app: FastAPI):
        await projects_frontend_main.startup(app)

    async def teardown(self, app: FastAPI):
        await projects_frontend_main.teardown(app)

    def mount(self, app: FastAPI):
        projects_frontend_main.mount(
            app, self.settings.api_host, self.settings.api_port
        )
