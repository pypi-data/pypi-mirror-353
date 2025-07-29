from .._app import AppBackend, AppFrontend, FastAPI

from .backend import main as floors_backend_main

from .frontend import main as floors_frontend_main


class FloorsBackend(AppBackend):
    async def startup(self, app: FastAPI):
        await floors_backend_main.startup(app)

    async def teardown(self, app: FastAPI):
        await floors_backend_main.teardown(app)

    def mount(self, app: FastAPI):
        floors_backend_main.mount(app)


class FloorsFrontend(AppFrontend):
    async def startup(self, app: FastAPI):
        await floors_frontend_main.startup(app)

    async def teardown(self, app: FastAPI):
        await floors_frontend_main.teardown(app)

    def mount(self, app: FastAPI):
        floors_frontend_main.mount(app, self.settings.api_host, self.settings.api_port)
