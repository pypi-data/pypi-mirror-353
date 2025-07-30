from nicegui import ui, app

from ..settings import PyFostSettings

settings = PyFostSettings()


async def load_colors_from_settings():
    await apply_colors(dark=app.storage.user.get("dark_mode", False))


async def apply_colors(dark: bool | None = False):
    # Needed to apply colors:
    await ui.context.client.connected()

    if dark:
        theme = settings.colors.dark.model_dump()
    else:
        theme = settings.colors.light.model_dump()
    ui.colors(**theme)


async def dark_mode_switch():
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, "dark_mode")

    async def switch(e):
        dark.toggle()
        await apply_colors(dark=dark.value)
        if dark.value:
            e.sender.props("icon=sym_o_light_mode")
        else:
            e.sender.props("icon=sym_o_dark_mode")

    ui.button(icon="sym_o_light_mode", on_click=switch).props("fab")
