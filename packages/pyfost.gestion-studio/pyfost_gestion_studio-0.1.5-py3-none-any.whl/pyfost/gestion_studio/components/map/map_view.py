from typing import Callable

from nicegui import ui, app

from ..zoomable import Zoomable
from .isvg import ISvg

from .generate_svg import generate_svg, backend_entities


async def map_view(
    initial_size=(500, 500),
    on_click=None,
    svg_content=None,
    tools: Callable | None = None,
    on_resized: Callable | None = None,
):
    """
    tools: awaitable called to render view's header left space
    view_index: used to fetch/store the default width for the view
    """
    svg_initial_content = svg_content
    if svg_initial_content is None:
        svg_initial_content = generate_svg(
            backend_entities, initial_size[0], initial_size[1]
        )
    else:
        svg_initial_content = (
            # f'<svg height="{h}px" width="{w}px" '
            f'<svg height="100%" width="100%" '
            + svg_initial_content.split("<svg", 1)[-1]
        )
    print(f"===================\n{svg_initial_content}\n=================")

    def handle_svg_click(element_data: dict):
        if on_click is not None:
            on_click(element_data)
            return
        info_str = (
            f"Clicked! ID: {element_data.get('id', 'N/A')}, "
            f"Tag: {element_data.get('tagName', 'N/A')}, "
            f"Classes: {', '.join(element_data.get('classList', []))}"
        )
        # clicked_info_label.set_text(info_str)
        if 0:
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
            isvg.update_style_by_id(el_id, "style", f"--seat-seat-color: {new_fill}")

    # with (
    #     ui.splitter()
    #     .classes("size-auto bg-red")
    #     .bind_value(app.storage.user, f"floormap_split_{view_index}") as splitter
    # ):
    # with ui.column().classes("xw-full"):
    with Zoomable(initial_size=initial_size, on_resized=on_resized):
        # with splitter.after:
        #     ui.label("test").classes("bg-green")
        # with splitter.separator:
        #     ui.icon("sym_o_arrow_range")  # .classes("text-green")
        # with splitter.before:

        with ui.column(align_items="center").classes("w-full gap-0"):
            with ui.row().classes("w-full gap-0"):
                if tools is not None:
                    await tools()

                ui.space()

                # ui.button(icon="zoom_out", on_click=lambda e: isvg.zoom_out()).props(
                #     "dense"
                # )
                ui.button(
                    icon="fit_screen", on_click=lambda e: isvg.zoom_reset()
                ).props("dense")
                # ui.button(icon="zoom_in", on_click=lambda e: isvg.zoom_in()).props(
                #     "dense"
                # )

            with ui.row().classes("w-full m-0 p-0 gap-0"):
                isvg = ISvg(
                    svg_content=svg_initial_content,
                    # clickable_elements_query=".clickable",
                    on_element_click=handle_svg_click,
                )  # .classes("w-full h-full")

            # ui.separator().classes("my-4")
            # with ui.row().classes("items-center gap-2"):
            #     ui.label("Target Class:").classes("text-lg")
            #     target_class_input = ui.input(value="zone").classes("w-32")
            #     class_opacity_slider = ui.slider(
            #         min=0,
            #         max=1,
            #         step=0.05,
            #         value=0.7,
            #         on_change=lambda e: isvg.update_style_by_class(
            #             target_class_input.value, "fill-opacity", e.value
            #         ),
            #     ).props('label-always markers step="0.1"')
            #     ui.label().bind_text_from(
            #         class_opacity_slider, "value", lambda v: f"Opacity: {v:.2f}"
            #     )
