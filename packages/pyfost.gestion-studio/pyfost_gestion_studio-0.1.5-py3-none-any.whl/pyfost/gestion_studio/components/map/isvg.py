from typing import Coroutine, Callable, Any

import time

from nicegui.element import Element
from nicegui import events
from typing import Optional, Dict, Any, Callable, List

AsyncFunc = Callable[[], Coroutine[Any, Any, None]]


class ISvg(Element, component="isvg.js"):

    def __init__(
        self,
        svg_content: str,
        initial_id_styles: Optional[Dict[str, Dict[str, Any]]] = None,
        initial_class_styles: Optional[Dict[str, Dict[str, Any]]] = None,
        clickable_elements_query: Optional[
            str
        ] = None,  # CSS selector for clickable elements
        on_element_click: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> None:
        """
        A custom NiceGUI element to display and interactively style SVG content.
        """
        super().__init__()
        self._classes.append("w-full")
        self._props["svgContent"] = svg_content
        self._props["idStyles"] = (
            initial_id_styles if initial_id_styles is not None else {}
        )
        self._props["classStyles"] = (
            initial_class_styles if initial_class_styles is not None else {}
        )
        if clickable_elements_query:
            self._props["clickableElementsQuery"] = clickable_elements_query
        self._props["zoomLevel"] = 1
        self._props["panningEnabled"] = True

        if on_element_click:
            # The event name 'element_click' must match the one emitted by this.$emit in Vue
            self.on(
                "element_click",
                lambda event_args: self._handle_element_click(
                    event_args, on_element_click
                ),
                # Pass the raw arguments from Vue. The `args` property of GenericEventArguments
                # will contain the dictionary {id, tagName, classList}.
                args=[None],
            )  # We expect one argument from the Vue event

    def _handle_element_click(
        self,
        event_args: events.GenericEventArguments,
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """Internal handler to process the click event and call the user's callback."""
        # event_args.args should be the dictionary sent from Vue
        # For example: {'id': 'rect1', 'tagName': 'rect', 'classList': ['shape', 'interactive']}
        if callback:
            # We pass the dictionary directly to the user's callback for convenience
            callback(event_args.args)

    @property
    def panning(self) -> bool:
        return self._props.get("panningEnabled", False)

    @panning.setter
    def panning(self, value: bool) -> None:
        self._props["panningEnabled"] = value
        self.update()

    def update_style_by_id(self, element_id: str, attribute: str, value: Any) -> None:
        current_styles = self._props["idStyles"].get(element_id, {})
        current_styles[attribute] = str(value)
        self._props["idStyles"][element_id] = current_styles
        self.update()

    def set_styles_for_id(self, element_id: str, styles: Dict[str, Any]) -> None:
        self._props["idStyles"][element_id] = {k: str(v) for k, v in styles.items()}
        self.update()

    def remove_styles_for_id(self, element_id: str) -> None:
        if element_id in self._props["idStyles"]:
            del self._props["idStyles"][element_id]
            self.update()

    def update_style_by_class(
        self, class_name: str, attribute: str, value: Any
    ) -> None:
        current_styles = self._props["classStyles"].get(class_name, {})
        current_styles[attribute] = str(value)
        self._props["classStyles"][class_name] = current_styles
        self.update()

    def set_styles_for_class(self, class_name: str, styles: Dict[str, Any]) -> None:
        self._props["classStyles"][class_name] = {k: str(v) for k, v in styles.items()}
        self.update()

    def remove_styles_for_class(self, class_name: str) -> None:
        if class_name in self._props["classStyles"]:
            del self._props["classStyles"][class_name]
            self.update()

    def update_text_content(self, element_id: str, text: str) -> None:
        self.run_method("updateTextContent", element_id, text)

    def update_svg_content(self, new_svg_content: str) -> None:
        self._props["svgContent"] = new_svg_content
        self.update()

    @property
    def id_styles(self) -> Dict[str, Dict[str, Any]]:
        return self._props["idStyles"]

    @id_styles.setter
    def id_styles(self, styles: Dict[str, Dict[str, Any]]) -> None:
        self._props["idStyles"] = styles
        self.update()

    @property
    def class_styles(self) -> Dict[str, Dict[str, Any]]:
        return self._props["classStyles"]

    @class_styles.setter
    def class_styles(self, styles: Dict[str, Dict[str, Any]]) -> None:
        self._props["classStyles"] = styles
        self.update()

    def fit_view(self):
        self._props["fitViewRequest"] = (
            time.time()
        )  # Ugly, but I don't know how to call js method from here :sweat:
        self.update()

    def zoom_reset(self):
        self._props["fitViewRequest"] = time.time()
        self.update()
