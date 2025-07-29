from typing import Dict, List, Optional

import os

from lxml import etree
import svgwrite


def extract_svg_defs(svg_content: str) -> Dict[str, List[Dict]]:
    """
    Extract all definitions from SVG content string.

    Args:
        svg_content (str): The SVG content as a string

    Returns:
        Dict containing organized defs data:
        {
            'symbols': [{'id': str, 'title': str|None, 'viewBox': str, 'content': str, 'element': Element}, ...],
            'gradients': [{'id': str, 'title': str|None, 'type': str, 'content': str, 'element': Element}, ...],
            'patterns': [{'id': str, 'title': str|None, 'content': str, 'element': Element}, ...],
            'clipPaths': [{'id': str, 'title': str|None, 'content': str, 'element': Element}, ...],
            'masks': [{'id': str, 'title': str|None, 'content': str, 'element': Element}, ...],
            'markers': [{'id': str, 'title': str|None, 'content': str, 'element': Element}, ...],
            'filters': [{'id': str, 'title': str|None, 'content': str, 'element': Element}, ...],
            'other': [{'id': str, 'title': str|None, 'tag': str, 'content': str, 'element': Element}, ...]
        }
    """

    try:
        # Parse the SVG content
        tree = etree.fromstring(svg_content.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid SVG content: {e}")

    # Define namespaces
    namespaces = {
        "svg": "http://www.w3.org/2000/svg",
        "xlink": "http://www.w3.org/1999/xlink",
    }

    # Initialize result structure
    defs_data = {
        "symbols": [],
        "gradients": [],
        "patterns": [],
        "clipPaths": [],
        "masks": [],
        "markers": [],
        "filters": [],
        "other": [],
    }

    # Find all defs sections
    defs_sections = tree.xpath("//svg:defs", namespaces=namespaces)

    for defs_section in defs_sections:
        # Process each child element in defs
        for child in defs_section:
            element_id = child.get("id")
            title = child.findtext("svg:title", namespaces=namespaces)
            element_content = etree.tostring(
                child, encoding="unicode", pretty_print=True
            )

            # Remove namespace prefixes from tag name for easier matching
            tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            # Organize by element type
            if tag_name == "symbol":
                defs_data["symbols"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "viewBox": child.get("viewBox"),
                        "content": element_content,
                        "element": child,
                    }
                )

            elif tag_name in ["linearGradient", "radialGradient"]:
                defs_data["gradients"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "type": tag_name,
                        "content": element_content,
                        "element": child,
                    }
                )

            elif tag_name == "pattern":
                defs_data["patterns"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "content": element_content,
                        "element": child,
                    }
                )

            elif tag_name == "clipPath":
                defs_data["clipPaths"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "content": element_content,
                        "element": child,
                    }
                )

            elif tag_name == "mask":
                defs_data["masks"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "content": element_content,
                        "element": child,
                    }
                )

            elif tag_name == "marker":
                defs_data["markers"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "content": element_content,
                        "element": child,
                    }
                )

            elif tag_name == "filter":
                defs_data["filters"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "content": element_content,
                        "element": child,
                    }
                )

            else:
                # Any other elements in defs
                defs_data["other"].append(
                    {
                        "id": element_id,
                        "title": title,
                        "tag": tag_name,
                        "content": element_content,
                        "element": child,
                    }
                )

    return defs_data


def print_defs_summary(defs_data: Dict) -> None:
    """
    Print a summary of extracted defs.

    Args:
        defs_data: The result from extract_svg_defs()
    """
    print("=" * 40)
    print("SVG Defs Summary:")
    print("=" * 40)

    for category, items in defs_data.items():
        if items:
            print(f"\n{category.upper()}:")
            for item in items:
                id_str = f" (id: {item['id']})" if item["id"] else " (no id)"
                title = item["title"]
                if category == "gradients":
                    print(f"  - {item['type']}{id_str} {title}")
                elif "tag" in item:
                    print(f"  - {item['tag']}{id_str} {title}")
                else:
                    print(f"  - {category[:-1]}{id_str} {title}")
