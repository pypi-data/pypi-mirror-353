import os

from .usages import extract_svg_usages, print_usage_summary
from .defs import (
    extract_svg_defs,
    print_defs_summary,
)

_TEMPLATE_CONTENT: str | None = None
_EXAMPLE_CONTENT: str | None = None


def get_template_content() -> str:
    global _TEMPLATE_CONTENT

    if _TEMPLATE_CONTENT is None:
        template_filename = os.path.normpath(
            os.path.join(__file__, "..", "..", "map_TEMPLATE.svg")
        )
        with open(template_filename, "r") as f:
            _TEMPLATE_CONTENT = f.read()

    return _TEMPLATE_CONTENT


def get_example_content() -> str:
    global _EXAMPLE_CONTENT

    if _EXAMPLE_CONTENT is None:
        template_filename = os.path.normpath(
            os.path.join(__file__, "..", "..", "map_example.svg")
        )
        with open(template_filename, "r") as f:
            _EXAMPLE_CONTENT = f.read()

    return _EXAMPLE_CONTENT


def translate_svg(svg_content: str) -> str:
    svg_content = get_example_content()  # TODO: stop using test content

    # Extract template defs
    template_defs = extract_svg_defs(get_template_content())
    print_defs_summary(template_defs)
    print_usage_summary(extract_svg_usages(get_template_content()))
    return ""

    # Extract defs from svg to translate
    defs = extract_svg_defs(svg_content)
    _print_defs_summary(defs)

    usage = extract_svg_usages(svg_content)
    _print_usage_summary(usage)
    # _get_all_referenced_ids(usage)

    # Access specific data
    print(f"\nFound {len(template_defs['symbols'])} symbols:")
    for symbol in template_defs["symbols"]:
        print(f"  - Symbol ID: {symbol['id']} TITLE: {symbol['title']}")
        print(f"    ViewBox: {symbol['viewBox']}")

    # template_content = get_template_content()
    # template_data = SVGTranslator().analyze_user_svg
    #     my_symbols_library={'my-icon': {}, 'my-shape': {}},
    #     my_styles_library={'my-gradient-1': {}, 'my-color-1': {}}
    # )

    # # Process user SVG
    # user_svg_content = open('user_file.svg').read()
    # usage_data = translator.analyze_user_svg(user_svg_content)
    # mapped_data = translator.map_to_my_definitions(usage_data)
    # translator.generate_new_svg(mapped_data, 'output.svg')


def test():
    svg_content = get_example_content()  # TODO: stop using test content

    template_svg = get_template_content()
    # debug_svg_elements(template_svg)
    template_defs = extract_svg_defs(template_svg)
    # print_defs_summary(template_defs)

    # debug_svg_elements(svg_content)
    content_defs = extract_svg_defs(svg_content)
    # print_defs_summary(content_defs)
    usages = extract_svg_usages(svg_content)
    print_usage_summary(usages)

    return

    # Get all referenced IDs
    all_refs = get_all_referenced_ids(usages)
    print(f"\nAll referenced IDs: {sorted(all_refs)}")

    # Access specific data
    print(f"\nFound {len(usages['symbol_uses'])} symbol uses:")
    for use in usages["symbol_uses"]:
        print(f"  - Using #{use['ref']} at position ({use['x']}, {use['y']})")


if __name__ == "__main__":
    test()
