from .._app import AppFrontend, FastAPI

from .main import startup, teardown, mount


class HomeFrontend(AppFrontend):
    async def startup(self, app: FastAPI):
        await startup(app)

    async def teardown(self, app: FastAPI):
        await teardown(app)

    def mount(self, app: FastAPI):
        mount(app, self.settings.api_host, self.settings.api_port)
