import time

from nicegui import ui, app

from ..components.header import header, default_header_tools_renderer, tool_button
from ..components.link_lists import big_button_links, LinkInfo

from ..settings import PyFostSettings

from .home_config_page import get_home_config

settings = PyFostSettings()


@ui.page("/settings")
async def settings_page():
    await header("Gestion Studio [User Settings]")

    await ui.context.client.connected()

    storage_names = ["general", "user", "browser", "tab"]
    with ui.column().classes("w-full"):
        for storage_name in storage_names:
            with ui.expansion(value=True).classes("w-full") as expansion:
                with expansion.add_slot("header"):
                    ui.markdown(f"### {storage_name.title()}").classes("w-full")
                    # ui.image('https://nicegui.io/logo.png').classes('w-16')
                try:
                    storage = getattr(app.storage, storage_name)
                except Exception as err:
                    ui.label(f"Unaccessible: {err}")
                else:
                    if not storage:
                        ui.label(f"No data defined in {storage_name!r} storage.")
                    for k, v in storage.items():
                        input = ui.input(k, value=v).bind_value(storage, k)
                        if k in ("id",):
                            input.disable()

    def do_it(e):
        app.storage.general["Test"] = time.time()
        app.storage.user["Test"] = time.time()
        # app.storage.browser["Test"] = time.time()
        app.storage.tab["Test"] = time.time()

    ui.button("Set Test values", on_click=do_it)


async def home_page():
    async def goto_home_config():
        ui.navigate.to("/home-config")

    async def tools_renderer():
        tool_button(icon="sym_o_settings", on_click=goto_home_config)
        await default_header_tools_renderer()

    await header("Gestion Studio", None, header_tools_renderer=tools_renderer)
    config = await get_home_config()

    custom_links = []
    for link in config.custom_links:
        custom_links.append(
            LinkInfo(
                label=link.label,
                icon_name=link.icon_name,
                target=link.target,
                new_tab=link.new_tab,
            )
        )

    pages = [
        custom_links,
        [
            LinkInfo(
                label="Floor Plans", icon_name="sym_o_explore", target="apps/floors/"
            ),
            LinkInfo(
                label="Projects",
                icon_name="sym_o_interactive_space",
                target="apps/projects/",
            ),
        ],
        [
            LinkInfo(label="Settings", icon_name="sym_o_handyman", target="settings"),
            LinkInfo(label="API", icon_name="auto_fix_high", target="/docs"),
        ],
    ]
    big_button_links(pages)
