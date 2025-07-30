raise Exception("OBSOLETE")

import pathlib
from nicegui import ui
from .map_view import map_view

# (Make sure InteractiveSvg class definition is above or imported)
# (Make sure interactive_svg_component.js is in the same directory)
from .isvg import ISvg

from .generate_svg import generate_svg, backend_entities

from ..header import header

svg_initial_content = generate_svg(backend_entities, 1500, 400)
# with open(pathlib.Path(__file__ + "/../example_map.svg").resolve(), "r") as fp:
#     svg_initial_content = fp.read()

xsvg_initial_content = """
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg" style="border: 1px solid #ccc;">
    <rect id="rect1" x="10" y="10" width="80" height="80" fill="blue" class="shape interactive clickable" />
    <circle id="circle1" cx="150" cy="50" r="40" fill="green" class="shape non-clickable" />
    <rect id="rect2" x="10" y="100" width="80" height="80" fill="lightblue" class="shape interactive clickable" />
    <g id="group1" class="clickable">
    <text x="150" y="120" id="text1" font-family="Verdana" font-size="20" fill="purple">Click Me (Text)</text>
    <rect x="140" y="100" width="120" height="30" fill="rgba(0,0,0,0.1)" />
    </g>
    <text x="10" y="190" id="text_non_clickable" fill="gray">Not Clickable</text>
</svg>
"""

# from nicegui import ui, app, events # Make sure to import events

# (InteractiveSvg class definition and interactive_svg_component.js should be available)


@ui.page("/map_test")
async def map_page():
    ui.label("Interactive SVG with Click Events").classes("text-h5")

    xsvg_initial_content = """
    <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg" style="border: 1px solid #ccc;">
      <rect id="rect1" x="10" y="10" width="80" height="80" fill="blue" class="shape interactive clickable" />
      <circle id="circle1" cx="150" cy="50" r="40" fill="green" class="shape non-clickable" />
      <rect id="rect2" x="10" y="100" width="80" height="80" fill="lightblue" class="shape interactive clickable" />
      <g id="group1" class="clickable">
        <text x="150" y="120" id="text1" font-family="Verdana" font-size="20" fill="purple">Click Me (Text)</text>
        <rect x="140" y="100" width="120" height="30" fill="rgba(0,0,0,0.1)" />
      </g>
      <text x="10" y="190" id="text_non_clickable" fill="gray">Not Clickable</text>
    </svg>
    """

    xsvg_initial_content = """
    <svg width="600" height="400" viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg" style="border: 1px solid #777;">
      <rect id="rect1" x="10" y="10" width="80" height="80" fill="blue" class="shape interactive clickable" />
      <circle id="circle1" cx="150" cy="50" r="40" fill="green" class="shape non-clickable" />
      <rect id="rect2" x="10" y="100" width="80" height="80" fill="lightblue" class="shape interactive clickable" />
      <g id="group1" class="clickable">
        <text x="150" y="120" id="text1" font-family="Verdana" font-size="20" fill="purple">Click Me (Text)</text>
        <rect x="140" y="100" width="120" height="30" fill="rgba(0,0,0,0.05)" />
      </g>
      <text x="10" y="190" id="text_non_clickable" fill="gray">Not Clickable</text>
    </svg>
    """

    clicked_info_label = ui.label("Clicked element info will appear here.")

    def handle_svg_click(element_data: dict):
        # element_data is the dictionary: {'id': ..., 'tagName': ..., 'classList': ...}
        info_str = (
            f"Clicked! ID: {element_data.get('id', 'N/A')}, "
            f"Tag: {element_data.get('tagName', 'N/A')}, "
            f"Classes: {', '.join(element_data.get('classList', []))}"
        )
        clicked_info_label.set_text(info_str)
        ui.notify(
            f"Python received click on: {element_data.get('id') or element_data.get('tagName')}",
            type="info",
        )

        # Example: Change color of the clicked element if it has an ID
        el_id = element_data.get("id")
        if el_id:
            # Cycle through some colors
            import random

            current_fill = random.choice(["yellow", "orange", "red"])
            new_fill = "yellow"
            if current_fill == "yellow":
                new_fill = "orange"
            elif current_fill == "orange":
                new_fill = "red"
            # interactive_svg.update_style_by_id(el_id, "fill", new_fill)
            # interactive_svg.update_style_by_id(el_id, "stroke", new_fill)
            interactive_svg.update_style_by_id(
                el_id, "style", f"--seat-seat-color: {new_fill}"
            )

    interactive_svg = ISvg(
        svg_content=svg_initial_content,
        # Only elements with class "clickable" or elements within them will trigger the event
        # If you click on "text1", it will be caught because its parent "group1" is "clickable"
        clickable_elements_query=".clickable",
        on_element_click=handle_svg_click,
    ).classes("w-full border-2 border-gray-300 p-2 rounded-md shadow-lg")

    ui.separator().classes("my-4")
    with ui.row().classes("items-center gap-2"):
        ui.button("Zoom +", on_click=lambda e: interactive_svg.zoom_in())
        ui.button("Zoom -", on_click=lambda e: interactive_svg.zoom_out())

    ui.separator().classes("my-4")
    with ui.row().classes("items-center gap-2"):
        ui.label("Target ID:").classes("text-lg")
        target_id_input = ui.input(value="rect1").classes("w-32")
        fill_color_picker = ui.color_input(
            label="Fill",
            value="#FF5733",
            on_change=lambda e: interactive_svg.update_style_by_id(
                target_id_input.value, "fill", e.value
            ),
        )
        stroke_width_input = ui.number(
            label="Stroke Width",
            value=1,
            min=0,
            step=0.5,
            format="%.1f",
            on_change=lambda e: interactive_svg.update_style_by_id(
                target_id_input.value, "stroke-width", e.value
            ),
        )

    ui.separator().classes("my-4")
    with ui.row().classes("items-center gap-2"):
        ui.label("Target Class:").classes("text-lg")
        target_class_input = ui.input(value="interactive").classes("w-32")
        class_opacity_slider = ui.slider(
            min=0,
            max=1,
            step=0.05,
            value=0.7,
            on_change=lambda e: interactive_svg.update_style_by_class(
                target_class_input.value, "opacity", e.value
            ),
        ).props('label-always markers step="0.1"')
        ui.label().bind_text_from(
            class_opacity_slider, "value", lambda v: f"Opacity: {v:.2f}"
        )

    ui.separator().classes("my-4")
    with ui.row().classes("items-center gap-2"):
        ui.label("Text for #text1:").classes("text-lg")
        text_content_input = ui.input(
            value="Hello NiceGUI SVG!",
            on_change=lambda e: interactive_svg.update_text_content("text1", e.value),
        ).classes("flex-grow")

    ui.separator().classes("my-4")
    with ui.row().classes("items-center gap-2"):
        ui.button(
            "Reset rect1 styles",
            on_click=lambda: interactive_svg.remove_styles_for_id("rect1"),
        )
        ui.button(
            "Make .shape red",
            on_click=lambda: interactive_svg.set_styles_for_class(
                "shape", {"fill": "red"}
            ),
        )


@ui.page("/map")
async def map_page():
    await header("Floormap Test")

    @ui.refreshable
    def info(data):
        if "id" not in data:
            ui.label("Select something to view its properties.")
            return
        with ui.column():
            ui.markdown(f"# {data['id']}")
            ui.input("Type", value=data.get("tagName"))

            classes: list[str] = [
                v for v in data.get("classList") if not v.startswith("isvg_")
            ]
            ui.input("Classes", value=classes)
            # fields = ["tagName", "classList"]
            # for field in fields:
            #     ui.input(field, value=data.get(field))

        # ui.label(f"infos: {data}")

    def on_click(element):
        info.refresh(element)

    with ui.row(wrap=False):
        map_view(on_click=on_click)
        map_view(on_click=on_click)
        info({})
