import svgwrite
import svgwrite.container
import svgwrite.path
import svgwrite.text


# Dummy entity data
backend_entities = {
    "bg": [
        dict(
            id="wall_001",
            type="path",
            fill="white",
            stroke="blue",
            d="M 14.1 6.337 L 12.752 158.175 L 166.388 196.809 L 212.209 148.293 L 321.82 171.652 L 325.414 8.134 L 14.1 6.337 Z",
        ),
        dict(
            id="zone_001",
            type="path",
            fill="yellow",
            stroke="red",
            d="M 23.108 12.4 L 21.647 93.496 L 180.313 94.835 L 180.762 50.902 L 88.299 52.03 L 90.379 13.072 L 23.108 12.4 Z",
        ),
    ],
    "mg": [
        dict(
            id="seat1",
            type="symbol",
            href="#SEAT",
            classes="clickable",
            x=50,
            y=50,
            rot=0,
        ),
        dict(
            id="seat2",
            type="symbol",
            href="#SEAT",
            classes="clickable",
            x=150,
            y=100,
            category="B",
            rot=90,
        ),
        dict(
            id="seat3",
            type="symbol",
            href="#SEAT",
            classes="clickable",
            x=100,
            y=180,
            category="A",
            rot=-90,
        ),
        dict(
            id="seat4",
            type="symbol",
            href="#SEAT",
            classes="clickable",
            x=250,
            y=70,
            category="C",
            rot=180,
        ),
    ],
    "fg": [
        dict(
            id="table_001",
            type="symbol",
            href="#TABLE",
            x=250,
            y=80,
        ),
        dict(
            id="table_002",
            type="symbol",
            href="#TABLE",
            x=250,
            y=80,
        ),
    ],
}


#
#
# --- svgwrite
#
#


def generate_symbols(drawing: svgwrite.Drawing) -> None:

    # SEAT
    w = 30
    h = 45
    min_x = -w / 2
    min_y = -2 * (h / 3)
    symbol = drawing.symbol(
        id="SEAT",
        viewBox=f"{min_x} {min_y} {w} {h}",
    )
    symbol.add(
        drawing.rect(
            insert=(-2.495, -14.642),
            size=(5, 5),
            style="stroke-width: .5;",
            class_="seat-back-handle",
        ),
    )
    symbol.add(
        drawing.path(
            style="fill:  var(--seat-back-color, rgb(186, 218, 85)); stroke: rgb(0, 0, 0); stroke-width: 0.5; transform-origin: 0.018px -6.093px;",
            d="M -3.708 -22.926 H 3.717 A 4.7 4.7 0 0 1 8.417 -18.226 V -15.473 A 2 2 0 0 1 6.417 -13.473 H -6.408 A 2 2 0 0 1 -8.408 -15.473 V -18.226 A 4.7 4.7 0 0 1 -3.708 -22.926 Z",
            class_="seat-back",
        )
    )
    symbol.add(
        drawing.path(
            style="fill: var(--seat-seat-color, rgb(216, 216, 216)); stroke: rgb(0, 0, 0); stroke-width: 1; transform-origin: 0.018px -6.774px;",
            d="M -8.004 -10 H 8.015 A 2 2 0 0 1 10.015 -8 V 5 A 5 5 0 0 1 5.015 10 H -5.004 A 5 5 0 0 1 -10.004 5 V -8 A 2 2 0 0 1 -8.004 -10 Z",
            class_="seat-seat",
        )
    )
    symbol.add(
        drawing.path(
            style="fill: var(--seat-arm-color, rgb(186, 218, 85)); stroke: rgb(0, 0, 0); stroke-width: 0.5; transform-origin: 69.328px 199.997px;",
            d="M 57.878 198.596 H 61.807 A 1 1 0 0 1 62.807 199.596 V 210.596 A 2.965 3 0 0 1 59.843 213.596 H 59.843 A 2.965 3 0 0 1 56.878 210.596 V 199.596 A 1 1 0 0 1 57.878 198.596 Z",
            transform="matrix(1, -0.000076, 0.000074, 1, -69.30953444, -206.0896531)",
            class_="seat-left-arm",
        )
    )

    symbol.add(
        drawing.path(
            style="fill: var(--seat-arm-color, rgb(186, 218, 85)); stroke: rgb(0, 0, 0); stroke-width: 0.5; transform-origin: 50.297px 200.076px;",
            d="M 57.878 198.596 H 61.807 A 1 1 0 0 1 62.807 199.596 V 210.596 A 2.965 3 0 0 1 59.843 213.596 H 59.843 A 2.965 3 0 0 1 56.878 210.596 V 199.596 A 1 1 0 0 1 57.878 198.596 Z",
            transform="matrix(1, -0.000076, 0.000074, 1, -50.27851864, -206.16866634)",
            class_="seat-right-arm",
        )
    )

    symbol.add(
        drawing.rect(
            style="fill: var(--seat-selectbox-color, cyan); opacity: var(--seat-selectbox-opacity, 0);",
            insert=(min_x, min_y),
            size=(w, h),
        )
    )
    drawing.defs.add(symbol)


def add_path(drawing, parent, item):
    entity_id = item.get("id", "???")
    # group: svgwrite.container.Group = dwg.g(id=entity_id, class_="wall")
    path: svgwrite.path.Path = drawing.path(
        id=entity_id,
        fill=item["fill"],
        stroke=item["stroke"],
        d=item["d"],
    )
    parent.add(path)


def add_symbol(drawing, parent, item):
    w = 30
    h = 45
    entity_id = item.get("id", "???")
    classes = item.get("classes", "noclass")
    x = item["x"]
    y = item["y"]
    rot = item.get("rot", 0)
    g = drawing.g(
        id=entity_id,
        class_=classes,
        transform=f"translate({x}, {y}) rotate({rot}) scale(1)",
    )
    parent.add(g)

    g.add(
        drawing.use(
            href=item["href"],
            x=-w / 2,
            y=-h / 2,
            size=(w, h),
            stroke="black",
            stroke_width=1,
            id=entity_id,
            class_=item.get("classes", "noclass"),
            # style=f"--seat-seat-color: {color}",
        )
    )


def generate_svg(entities, svg_width, svg_height):
    """
    Generates an SVG string with a circle for each entity.

    :param entities: List of entity dictionaries. Expected keys: id, name, x, y, category.
    :param svg_width: Overall width of the SVG canvas.
    :param svg_height: Overall height of the SVG canvas.
    :return: SVG content as a string.
    """
    # dwg = svgwrite.Drawing(size=(f"{svg_width}px", f"{svg_height}px"))
    dwg = svgwrite.Drawing(size=("100%", "100%"))
    dwg.viewbox(0, 0, svg_width, svg_height)

    generate_symbols(dwg)

    if 1:
        # Add a background rectangle (optional)
        dwg.add(
            dwg.rect(
                insert=(0, 0), size=("100%", "100%"), fill="white", stroke="lightgray"
            )
        )

    layers = dwg.g(id="layers")
    dwg.add(layers)
    for layer_name in ("bg", "mg", "fg"):
        layer = dwg.g(id=f"{layer_name}.layer")
        layers.add(layer)
        for item in entities.get(layer_name, []):
            item_type = item["type"]
            if item_type == "symbol":
                i = item.copy()
                for ox in range(6):
                    i["x"] += ox * 50
                    for oy in range(5):
                        i["y"] += oy * 50
                        add_symbol(dwg, layer, i)
            elif item_type == "path":
                add_path(dwg, layer, item)

    if 0:
        walls_group = dwg.g(
            id="walls_layer",
            class_="wall immo",
        )
        dwg.add(walls_group)
        for entity in entities.get("walls", []):
            entity_id = entity.get("id", f"entity_{entity.get('name', 'unknown')}")
            group: svgwrite.container.Group = dwg.g(id=entity_id, class_="wall")
            path: svgwrite.path.Path = dwg.path(
                id=f"{entity_id}.path",
                fill=entity.get("fill", None),
                stroke=entity.get("stroke", None),
                d=entity.get("d", None),
            )
            group.add(path)
            walls_group.add(group)

        zones_group = dwg.g(
            id="zones_layer",
            class_="zone immo",
        )
        dwg.add(zones_group)
        for entity in entities.get("zones", []):
            entity_id = entity.get("id", f"entity_{entity.get('name', 'unknown')}")
            group: svgwrite.container.Group = dwg.g(id=entity_id, class_="zone")
            path: svgwrite.path.Path = dwg.path(
                id=f"{entity_id}.path",
                fill=entity.get("fill", None),
                stroke=entity.get("stroke", None),
                d=entity.get("d", None),
            )
            group.add(path)
            zones_group.add(group)

        seats_group = dwg.g(id="seats_layer")
        dwg.add(seats_group)
        for entity in entities.get("seats", []):
            w = 30
            h = 45
            entity_id = entity.get("id", f"entity_{entity.get('name', 'unknown')}")
            entity_name = entity.get("name", "N/A")
            x_pos = entity.get("x", 0)
            y_pos = entity.get("y", 0)
            rot = entity.get("rot", 0)
            g = dwg.g(
                id=entity_id,
                class_="seat clickable",
                transform=f"translate({x_pos}, {y_pos}) rotate({rot}) scale(1)",
            )
            seats_group.add(g)

            g.add(
                dwg.use(
                    href="#SEAT",
                    x=-w / 2,
                    y=-h / 2,
                    size=(w, h),
                    stroke="black",
                    stroke_width=1,
                    id=f"shape_{entity_id}",
                    class_="entity-shape",
                    # style=f"--seat-seat-color: {color}",
                )
            )

            g.add(
                dwg.text(
                    entity_name,
                    insert=(-w / 2, -2 * h / 3),
                    fill="black",
                    font_size="8px",
                    font_family="Arial",
                    id=f"text_{entity_id}",  # ID for the text
                    class_="entity-label",
                )
            )

    return dwg.tostring()
