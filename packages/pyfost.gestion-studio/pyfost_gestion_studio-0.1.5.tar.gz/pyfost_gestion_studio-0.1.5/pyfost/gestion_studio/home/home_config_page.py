from typing import Any

from pydantic import BaseModel
from nicegui import ui, app

from ..components.header import header
from ..components.icon_selector import IconSelector


class CustomLink(BaseModel):
    label: str
    target: str
    icon_name: str | None = None
    new_tab: bool = False


class HomeConfig(BaseModel):
    _refresh_ui_callback: Any = None  # FIXME: that annotation !!!

    custom_links: list[CustomLink] = []

    def add_cutom_link(self):
        link = CustomLink(label="My Link", target="/link-url")
        self.custom_links.append(link)
        self.save_config()

    def delete_custom_link(self, index: int):
        self.custom_links.pop(index)
        self.save_config()

    def save_config(self):
        app.storage.general["home-config"] = self.model_dump()
        if self._refresh_ui_callback is not None:
            self._refresh_ui_callback()


async def get_home_config() -> HomeConfig:
    config = HomeConfig(**app.storage.general.get("home-config", {}))
    print(config)
    return config


class CustomLinkEditor:
    def __init__(self, config: HomeConfig, index: int, custom_link: CustomLink) -> None:
        self.config = config
        self.index = index
        self.custom_link = custom_link

        self._label_input: ui.input | None = None
        self._target_input: ui.input | None = None
        self._icon_selector: IconSelector | None = None
        self._save_button: ui.button | None = None
        self._delete_button: ui.button | None = None

        self.build()

    def build(self):
        with ui.row(align_items="center").classes("w-full"):
            self._label_input = (
                ui.input(
                    "label", value=self.custom_link.label, on_change=self.on_changed
                )
                .on("keydown.enter", self.on_key_enter)
                .props("size=20")
            )
            self._target_input = (
                ui.input(
                    "target", value=self.custom_link.target, on_change=self.on_changed
                )
                .on("keydown.enter", self.on_key_enter)
                .props("size=80")
            )
            self._icon_selector = IconSelector(
                self.custom_link.icon_name, on_selected=self.on_changed
            )
            self._new_tab_checkbox = ui.checkbox(
                value=self.custom_link.new_tab, on_change=self.on_changed
            ).tooltip("Open in new tab?")

            with ui.row():
                self._save_button = (
                    ui.button(
                        icon="sym_o_save",
                        on_click=self.save_link,
                        color="positive",
                    )
                    .tooltip("Apply")
                    .props("dense")
                )
                self._save_button.set_visibility(False)

                self._delete_button = (
                    ui.button(
                        icon="sym_o_delete",
                        on_click=lambda i=self.index: self.config.delete_custom_link(i),
                        color="negative",
                    )
                    .tooltip("Delete")
                    .props("dense")
                )

    def on_changed(self):
        self._save_button.visible = True
        # self._delete_button.visible = False

    def on_key_enter(self):
        self.save_link()

    def save_link(self):
        # print("save", self.custom_link)
        self.custom_link.label = self._label_input.value
        self.custom_link.target = self._target_input.value
        self.custom_link.icon_name = self._icon_selector.current_icon
        self.custom_link.new_tab = bool(self._new_tab_checkbox.value)
        self.config.save_config()
        self._save_button.visible = False
        # self._delete_button.visible = True


@ui.refreshable
async def home_links_editor():
    config = await get_home_config()
    config._refresh_ui_callback = home_links_editor.refresh

    for index, link in enumerate(config.custom_links):
        CustomLinkEditor(config, index, link)

    ui.button(
        "Add custom link", icon="sym_o_add", on_click=config.add_cutom_link
    ).props("dense")


@ui.page("/home-config")
async def home_config_page():
    await header("Gestion Studio [Home Config]")

    with ui.row().classes("w-full"):
        ui.space()
        ui.markdown("### ⚠️ This is for Admins only ! ⚠️").classes("bg-red")
        ui.space()

    with ui.expansion(value=True).classes("w-full border") as expansion:
        with expansion.add_slot("header"):
            with ui.row(align_items="center").classes("w-full"):
                ui.icon("sym_o_link", size="xl")
                ui.markdown("### Home Links")
        await home_links_editor()
