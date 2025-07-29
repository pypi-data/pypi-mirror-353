from typing import Coroutine, Callable, Any

from nicegui import ui, app

from .theming import load_colors_from_settings, dark_mode_switch

AsyncFunc = Callable[[], Coroutine[Any, Any, None]]


def tool_button(*, icon: str, on_click):
    return ui.button(icon=icon, on_click=on_click).props("fab")


async def fullscreen_switch():
    fullscreen = ui.fullscreen()
    # Not a good idea: fullscreen.bind_value(app.storage.user, "fullscreen")

    def switch(e):
        fullscreen.toggle()
        if fullscreen.value:
            e.sender.props("icon=sym_o_fullscreen_exit")
        else:
            e.sender.props("icon=sym_o_fullscreen")

    tool_button(icon="sym_o_fullscreen", on_click=switch)
    # ui.button(icon="sym_o_fullscreen", on_click=switch).props("fab")


async def default_header_tools_renderer():
    await dark_mode_switch()
    await fullscreen_switch()


async def header(
    title: str | AsyncFunc,
    back_target: str | None = "/",
    back_icon: str = "sym_o_home",
    header_tools_renderer=None,
    *args,
    **kwargs,
):
    """
    If title is callable, it must be awaitable and accept *arg and **kwargs
    """
    await load_colors_from_settings()
    tools_renderer = header_tools_renderer or default_header_tools_renderer
    with ui.header(elevated=True):
        with ui.row(align_items="center").classes("w-full"):
            if back_target is not None:
                with ui.link(target=back_target):
                    ui.button(icon=back_icon).props("fab").classes("fg-secondary")
            with ui.row(align_items="baseline"):
                ui.image("/assets/fost_studio_logo_noborders.jpeg").classes("w-16")
                if isinstance(title, str):
                    ui.label(title).classes("text-h4 text-weight-bolder")
                else:
                    await title(*args, **kwargs)
            ui.space()
            await tools_renderer()
