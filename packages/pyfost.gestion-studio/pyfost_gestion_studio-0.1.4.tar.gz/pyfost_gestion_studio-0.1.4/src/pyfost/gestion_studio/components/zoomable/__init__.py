from typing import Callable

from nicegui import ui


class Zoomable(ui.element, component="zoomable.js"):
    EVENT_SIZE_CHANGED = "sizeChanged"

    def __init__(
        self,
        *,
        on_resized: Callable | None = None,
        initial_size: tuple[int, int] | None = None,
        border_width: str | None = None,
        border_color: str | None = None,
    ) -> None:
        super().__init__()
        if initial_size is not None:
            self._props["initialWidthProp"] = initial_size[0]
            self._props["initialHeightProp"] = initial_size[1]
        if border_width is not None:
            self._props["border_width"] = border_width
        if border_color is not None:
            self._props["border_color"] = border_color
        self.classes("border rounded-md shadow-lg")

        if on_resized is not None:
            self.on(self.EVENT_SIZE_CHANGED, on_resized)

    def border_width(self, width: str):
        self._props["border_width"] = width
        self.update()
        return self

    def border_color(self, color: str):
        self._props["border_color"] = color
        self.update()
        return self
