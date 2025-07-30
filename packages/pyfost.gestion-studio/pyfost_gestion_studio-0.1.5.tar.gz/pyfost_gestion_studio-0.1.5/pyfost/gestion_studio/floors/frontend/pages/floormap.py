import urllib.parse

from fastapi import Request
from starlette.datastructures import URL
from nicegui import ui, app, context

from ....components.header import header
from ....components.map.map_view import map_view

from .client import get_floors_client, models


class FloorsToShow:
    @classmethod
    def query_to_floors(cls, query) -> list[tuple[str, str]]:
        floors = urllib.parse.parse_qs(query).get("floors", [])
        floors = [i.split(":") for i in floors]
        return floors

    def __init__(self, maps_area, url: URL):
        self.url_path = url.path
        query = url.query
        self.maps_area = maps_area
        self._floors = self.query_to_floors(query)
        self._known_facilities = None

    async def known_facilities(self) -> list[models.Facility]:
        facilities = await get_floors_client().get_facilities()
        return facilities

    async def facility_floors(
        self, facility: models.Facility
    ) -> list[models.RelatedFloor]:
        if facility.id is None:
            raise ValueError(f"This Facility has not id: {facility}")
        facility = await get_floors_client().get_facility(facility_id=facility.id)
        return facility.floors

    def __len__(self) -> int:
        return len(self._floors)

    def __getitem__(self, index: int) -> tuple[str, str]:
        return self._floors[index]

    def __iter__(self):
        return iter(self._floors)

    def refresh_info(self):
        """
        Update the url and the maps area as if the page
        was reloaded.
        """
        # page = context.client.page
        # prefix = ""
        # if page.api_router is not None:
        #     prefix = page.api_router.prefix
        url = f"{self.url_path}?{self.to_params()}"
        ui.navigate.history.push(url)
        self.maps_area.refresh()

    def set(self, index, facility, floor):
        self._floors[index] = (facility, floor)
        self.refresh_info()

    def to_params(self):
        params = dict(floors=[f"{fa}:{fl}" for fa, fl in self._floors])
        return urllib.parse.urlencode(params, doseq=True)

    def add_floor(self, goto: bool = False):
        if self._floors:
            new_floor = self._floors[-1]
        else:
            # NB: adding an unexiting floor will show an empty map.
            # And there will not be a floor named '' in a facility
            # named "Select Floor"...
            # Right?
            # Oh god!
            new_floor = ("Select Floor", "")
        self._floors.append(new_floor)
        if goto:
            self.goto()
        else:
            self.refresh_info()

    def rem_floor(self, goto: bool = False):
        self._floors.pop(-1)
        if goto:
            self.goto()
        else:
            self.refresh_info()

    def goto(self):
        ui.navigate.to("?" + self.to_params())

    async def get_floor_svg(self, facility: str, floor: str):
        """
        Returns the svg map for the given facitlity name and floor name
        """
        api = get_floors_client()
        svg = ""
        print("----> FAC/FLO?", facility, floor)
        try:
            facility_id = await api.get_facility_id(facility)
        except Exception as err:
            print("!!!", err)
        else:
            print("-----------> FAC", facility_id)
            try:
                floor_id = await api.get_floor_id(facility_id, floor)
            except Exception as err:
                print("   !!!!", err)
            else:
                print("-----------> FLO", floor_id)
                svg = await get_floors_client().get_floor_svg(floor_id=floor_id)
        return svg


async def render_floor_selector(index, floors: FloorsToShow):
    current_facility, current_floor = floors[index]
    allow_add = False
    allow_rem = False
    if index == len(floors) - 1:
        allow_add = True
        if index > 0:
            allow_rem = True

    with ui.dropdown_button(f"{current_facility}:{current_floor}").props("dense"):
        for facility in await floors.known_facilities():
            ui.separator()
            with ui.row().classes("p-4 items-center"):
                ui.label(f"{facility.name}:").classes("text-h5 text-weigth-bold")
                for floor in await floors.facility_floors(facility):
                    chip_classes = " outline"
                    if (
                        facility.name == current_facility
                        and floor.name == current_floor
                    ):
                        chip_classes = ""

                    ui.chip(
                        floor.name,
                        on_click=lambda fa=facility.name, fl=floor.name: floors.set(
                            index, fa, fl
                        ),
                    ).props(
                        " " + chip_classes,
                    )

        ui.separator()
        with ui.row().classes("w-full"):
            if allow_rem:
                ui.button(
                    "Hide this floor",
                    icon="remove_circle",
                    on_click=lambda: floors.rem_floor(),
                )
            ui.space()
            if allow_add:
                ui.button(
                    "Add a floor",
                    icon="add_circle",
                    on_click=lambda: floors.add_floor(),
                )


async def floormap_page(
    request: Request,
):
    # we need this because we use app.storage.user:
    await ui.context.client.connected()

    @ui.refreshable
    async def maps_area():
        with ui.row().classes("w-full border-red"):
            if not len(floors):
                floors.add_floor(goto=False)
            for index, (facility, floor) in enumerate(floors):
                svg_content = await floors.get_floor_svg(facility, floor)
                storage_key = f"floomap_sizes_{index}"
                default_size = app.storage.user.get(storage_key, (500, 500))
                if not default_size:
                    # User may set the settings to 0 to clear default sizes 🤷🏻
                    default_size = (500, 500)

                async def map_view_tools(index=index):
                    await render_floor_selector(index, floors)

                async def on_resized(event, storage_key=storage_key):
                    size = event.args["width"], event.args["height"]
                    print(storage_key, size)
                    app.storage.user[storage_key] = size

                await map_view(
                    initial_size=default_size,
                    on_click=on_click,
                    svg_content=svg_content,
                    tools=map_view_tools,
                    on_resized=on_resized,
                )

    # we do the parsing ourselves to support "?floors=FACILITY_NAME:FLOOR_NAME&floors=FACILITY_NAME:FLOOR_NAME"
    # FIXME: backend should ensure that either facility name or floor name cannot contains a ':'
    floors = FloorsToShow(maps_area, request.url)

    await header(
        "Floor Plan",
        back_target="/apps/floors/",
        back_icon="sym_o_arrow_circle_left",
    )

    @ui.refreshable
    def info(data):
        if "id" not in data:
            ui.label("Select a seat to view its properties.")
            return

        classes: list[str] = [
            v for v in data.get("classList") if not v.startswith("isvg_")
        ]
        if not classes:
            ui.label("Select something interesting to view its properties.")
            return

        with ui.column():  # .classes("bg-red"):
            ui.markdown(f"# {classes[0]} {data['id'] or '???'}")
            ui.input("Type", value=data.get("tagName"))

            ui.input("Classes", value=classes)  # type: ignore (ui.input wrong annotation)

    def on_click(element):
        classes = [v for v in element.get("classList") if not v.startswith("isvg_")]
        if classes:
            info.refresh(element)

    with ui.row(wrap=False).classes("w-full"):
        await maps_area()  # type: ignore (calling ui.refreshable)

    with ui.right_drawer(elevated=True):
        info({})
