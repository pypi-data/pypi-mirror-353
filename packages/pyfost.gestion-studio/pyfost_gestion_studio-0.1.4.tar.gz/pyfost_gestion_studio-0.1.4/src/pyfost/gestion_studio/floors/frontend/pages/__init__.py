from nicegui import ui
from fastapi import APIRouter

# from ....components.theming import apply_colors, dark_mode_switch
from ....components.header import header
from ....components.link_lists import big_button_links, LinkInfo
from ...api import FloorsAPI, models

from .client import init_floors_client, get_floors_client, models
from .floormap import floormap_page


pages_router = APIRouter()


ui.page("/floormap", api_router=pages_router)(floormap_page)


@ui.page(path="/", api_router=pages_router, title="Floor Plans")
async def floors_home():
    await header("Floor Plans")
    facilities = await get_floors_client().get_facilities()
    facility_links = []
    for facility in facilities:
        facility_links.append(
            LinkInfo(
                label=facility.name,
                icon_name="sym_o_map",
                target=f"floormap?floors={facility.name}%3ARdC",
            )
        )

    pages = (
        [
            LinkInfo(label="Départs/Arrivées", icon_name="sym_o_sync_alt", target=""),
            LinkInfo(label="Stats & Charts", icon_name="sym_o_query_stats", target=""),
        ],
        facility_links,
        [
            LinkInfo(
                label="Admin", icon_name="sym_o_admin_panel_settings", target="admin"
            ),
            LinkInfo(label="Settings", icon_name="sym_o_handyman", target=""),
        ],
    )
    big_button_links(pages)


def mount_pages(parent_router: APIRouter, api_host: str, api_port: int):
    init_floors_client(api_host, api_port)
    parent_router.include_router(pages_router)
