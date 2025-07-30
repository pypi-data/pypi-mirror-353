from typing import Collection

from pydantic import BaseModel
from nicegui import ui


class LinkInfo(BaseModel):
    label: str
    icon_name: str | None = None
    target: str
    new_tab: bool = False  # FIXME: add support for that!


def big_button_links(pages: Collection[Collection[LinkInfo]]):
    """
    pages = [
        [LinkInfo, LinkInfo, LinkInfo, ...],
        [LinkInfo, LinkInfo, LinkInfo, ...],
        [LinkInfo, LinkInfo, LinkInfo, ...],
    ]
    """
    with ui.column(align_items="center").classes("p-8 w-full bg-box1"):
        for pages_group in pages:
            with ui.row().classes("bg-box2"):
                # for title, icon, target in pages_group:
                for link_info in pages_group:
                    with ui.card().classes("gap-0"):
                        with ui.row().classes("w-full"):
                            ui.space()
                            with ui.link(
                                target=link_info.target, new_tab=link_info.new_tab
                            ).classes("!no-underline"):
                                with ui.column(align_items="center"):
                                    ui.icon(
                                        link_info.icon_name or "link",
                                        size="xl",
                                        color="primary",
                                    )
                                    ui.label(link_info.label).classes(
                                        "text-lg text-secondary"
                                    )
                            ui.space()
