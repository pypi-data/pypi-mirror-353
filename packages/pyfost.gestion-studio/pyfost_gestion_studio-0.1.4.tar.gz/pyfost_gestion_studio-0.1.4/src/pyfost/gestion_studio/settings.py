from pydantic import BaseModel, Field, AnyUrl, IPvAnyNetwork
from pydantic_settings import BaseSettings, SettingsConfigDict


from ._app import AppSettings, AppBackendSettings, AppFrontendSettings, AppAllSettings
from ._version import version

current_version = version


# class ServiceSettings(BaseModel):
#     title: str
#     description: str
#     version: str = current_version
#     host: IPvAnyNetwork = "0.0.0.0"
#     port: int = 8001
#     reload: bool = True


# class AppBackendSettings(ServiceSettings):
#     database_url: AnyUrl | None = None


# class AppFrontendSettings(ServiceSettings):
#     api_host: IPvAnyNetwork = "0.0.0.0"
#     api_port: int = 8001
#     nice_secret: str = "THIS_IS_NOT_A_SAFE_VALUE"


# class AppAllSettings(AppBackendSettings, AppFrontendSettings):
#     pass


class AppsSettings(BaseModel):
    home_frontend: AppFrontendSettings = AppFrontendSettings(
        title="Fost Gestion-Studio - Home",
        description="Landing page",
        port=8001,
    )

    floors_backend: AppBackendSettings = AppBackendSettings(
        title="Fost Gestion-Studio - Floors Backend",
        description="API for managing Seats assignements and Related Tasks.",
        port=8010,
    )
    floors_frontend: AppFrontendSettings = AppFrontendSettings(
        title="Fost Gestion-Studio - Floors Frontend",
        description="GUI for managing Users, Projects, and Tasks.",
        port=8011,
    )

    projects_backend: AppBackendSettings = AppBackendSettings(
        title="Fost Gestion-Studio - Projects Backend",
        description="API for managing Users, Projects, and Tasks.",
        port=8020,
    )
    projects_frontend: AppFrontendSettings = AppFrontendSettings(
        title="Fost Gestion-Studio - Projects Frontend",
        description="GUI for managing Users, Projects, and Tasks.",
        port=8021,
    )


class RuntimeSettings(BaseModel):
    backends: AppBackendSettings = AppBackendSettings(
        title="Fost Gestion-Studio - All Backends",
        description="A service with all Backend routes",
        port=8101,
    )
    frontends: AppFrontendSettings = AppFrontendSettings(
        title="Fost Gestion-Studio - All Frontends",
        description="A service with all Frontend routes",
        port=8002,
        api_port=8101,
    )
    all: AppAllSettings = AppAllSettings(
        title="Fost Gestion-Studio - All Apps",
        description="A service with all Fost apps",
        port=8090,
        api_port=8090,
    )


class ColorTheme(BaseModel):
    primary: str = "#fdc217"
    secondary: str = "#222"
    accent: str = "#9c27b0"
    dark: str = "#1d1d1d"
    dark_page: str = "oklch(27.4% 0.006 286.033)"  # zinc-800
    positive: str = "#21ba45"
    negative: str = "#c10015"
    info: str = "#31ccec"
    warning: str = "#f2c037"
    #
    box1: str = "oklch(96.7% 0.001 286.375)"  # zinc-100
    box2: str = "oklch(87.1% 0.006 286.286)"  # zinc-300
    box3: str = "oklch(55.2% 0.016 285.938)"  # zinc-500


class UIColors(BaseModel):
    dark: ColorTheme = ColorTheme(
        secondary="oklch(92% 0.004 286.32)",  # zinc-200
        box1="oklch(44.2% 0.017 285.786)",  # zinc-600
        box2="oklch(70.5% 0.015 286.067)",  # zinc-400
        box3="oklch(92% 0.004 286.32)",  # zinc-200
    )
    light: ColorTheme = ColorTheme()


class PyFostSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYFOST__",
        # This will cummulate all the .env files,
        # so .env.DEV always wins if it exits:
        env_file=(".env", ".env.ALL", ".env.PROD", ".env.DEV"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        # nested_model_default_partial_update=False,
    )

    apps: AppsSettings = Field(default_factory=AppsSettings)
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)

    colors: UIColors = Field(default_factory=UIColors)


def test():
    import os, pprint

    # os.environ["PYFOST__APPS__PROJECTS__HOST"] = "0.0.0.0"
    # os.environ["PYFOST__APPS__PROJECTS__PORT"] = "8002"

    settings = PyFostSettings()
    # pprint.pprint(settings.model_dump())

    # assert settings.apps.projects.port == 8002


if __name__ == "__main__":
    test()
