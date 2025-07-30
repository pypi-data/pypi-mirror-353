import cssutils
from lxml import etree
from typing import Dict, List, Optional, Any


def debug_svg_elements(svg_content: str) -> None:
    """
    Debug function to see what elements exist in the SVG and their attributes.

    Args:
        svg_content (str): The SVG content as a string
    """
    try:
        tree = etree.fromstring(svg_content.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        print(f"Invalid SVG content: {e}")
        return

    namespaces = {
        "svg": "http://www.w3.org/2000/svg",
        "xlink": "http://www.w3.org/1999/xlink",
    }

    print("SVG Debug Information:")
    print("=" * 50)

    # Show all elements with their attributes
    all_elements = tree.xpath("//*")
    print(f"\nFound {len(all_elements)} total elements:")

    for i, elem in enumerate(all_elements):
        tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        attrs = dict(elem.attrib)
        print(f"{i+1:2d}. <{tag_name}> - Attributes: {attrs}")

    # Check for CSS styles
    print(f"\nChecking for CSS and style content:")

    # Look for <style> tags
    style_tags = tree.xpath("//svg:style", namespaces=namespaces) + tree.xpath(
        "//style"
    )
    print(f"Found {len(style_tags)} <style> tags:")
    for i, style_tag in enumerate(style_tags):
        content = style_tag.text or ""
        print(f"  Style {i+1}: {len(content)} characters")
        if content.strip():
            print(f"    Content preview: {content[:200]}...")

    # Look for style attributes
    style_elements = tree.xpath("//*[@style]")
    print(f"\nFound {len(style_elements)} elements with style attributes:")
    for i, elem in enumerate(style_elements[:5]):  # Show first 5
        tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        style_val = elem.get("style", "")
        print(f'  {i+1}. <{tag_name}> style="{style_val}"')

    # Look for elements that might use fill/stroke through CSS classes
    elements_with_classes = tree.xpath("//*[@class]")
    print(f"\nFound {len(elements_with_classes)} elements with class attributes:")
    for i, elem in enumerate(elements_with_classes[:5]):  # Show first 5
        tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        class_val = elem.get("class", "")
        print(f'  {i+1}. <{tag_name}> class="{class_val}"')

    # Specifically test fill attribute queries
    print(f"\nTesting fill/stroke attribute queries:")

    queries = [
        ("//*[@fill]", "All elements with fill attribute"),
        ("//*[@stroke]", "All elements with stroke attribute"),
        ("//*[@style]", "All elements with style attribute"),
        ("//svg:*[@fill]", "SVG namespaced elements with fill"),
        ('//*[contains(@style, "fill")]', 'Elements with "fill" in style'),
        ('//*[contains(@style, "stroke")]', 'Elements with "stroke" in style'),
        ('//*[contains(@style, "url")]', 'Elements with "url" in style'),
        ("//svg:style", "SVG style elements"),
        ("//style", "Style elements"),
    ]

    for query, description in queries:
        try:
            if "svg:" in query:
                results = tree.xpath(query, namespaces=namespaces)
            else:
                results = tree.xpath(query)

            print(f"  {description}: {len(results)} matches")
            if results:
                for elem in results[:3]:  # Show first 3 matches
                    tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                    if tag == "style":
                        content = elem.text[:100] if elem.text else "No content"
                        print(f"    - <{tag}> content: {content}...")
                    else:
                        relevant_attrs = {
                            k: v
                            for k, v in elem.attrib.items()
                            if k in ["fill", "stroke", "style", "class", "id"]
                        }
                        print(f"    - <{tag}> {relevant_attrs}")

        except Exception as e:
            print(f"  {description}: ERROR - {e}")

    # Check for any URL patterns in the entire SVG content
    print(f"\nSearching for URL patterns in entire SVG content:")
    import re

    url_patterns = re.findall(r"url\(#([^)]+)\)", svg_content)
    if url_patterns:
        print(f"Found {len(url_patterns)} url(#...) patterns:")
        for pattern in set(url_patterns):  # Remove duplicates
            print(f"  - url(#{pattern})")
    else:
        print("No url(#...) patterns found in SVG content")


def extract_svg_usages(svg_content: str) -> Dict[str, List[Dict]]:
    """
    Extract all usage references from SVG content string.
    This includes <use> elements, fill/stroke references to defs, and other URL references.

    Args:
        svg_content (str): The SVG content as a string

    Returns:
        Dict containing organized usage data:
        {
            'symbol_uses': [{'ref': str, 'x': str, 'y': str, 'transform': str, 'class': str, 'element': Element}, ...],
            'fill_refs': [{'ref': str, 'element_tag': str, 'element_id': str, 'element': Element}, ...],
            'stroke_refs': [{'ref': str, 'element_tag': str, 'element_id': str, 'element': Element}, ...],
            'clip_path_refs': [{'ref': str, 'element_tag': str, 'element_id': str, 'element': Element}, ...],
            'mask_refs': [{'ref': str, 'element_tag': str, 'element_id': str, 'element': Element}, ...],
            'marker_refs': [{'ref': str, 'marker_type': str, 'element_tag': str, 'element': Element}, ...],
            'filter_refs': [{'ref': str, 'element_tag': str, 'element_id': str, 'element': Element}, ...],
            'pattern_refs': [{'ref': str, 'element_tag': str, 'element_id': str, 'element': Element}, ...],
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
    usage_data = {
        "symbol_uses": [],
        "fill_refs": [],
        "stroke_refs": [],
        "clip_path_refs": [],
        "mask_refs": [],
        "marker_refs": [],
        "filter_refs": [],
        "pattern_refs": [],
        # "other_refs": [],
    }

    def clean_tag_name(element):
        """Remove namespace prefix from tag name"""
        return element.tag.split("}")[-1] if "}" in element.tag else element.tag

    def find_element_title(element):
        title = element.findtext("svg:title", namespaces=namespaces)
        if title is None:
            title = element.findtext("title")
        return title

    def extract_attr_or_style_value(elem, name):
        """
        Return the value of the attribute of the given name,
        looking up in the style properties if needed
        """
        value = elem.get(name, None)
        if value is None:
            style = cssutils.parseStyle(elem.get("style"), validate=False)
            value = style[name]
        return value

    def extract_url_ref(value: str) -> Optional[str]:
        """Extract reference from url(#ref) format"""
        if value and value.startswith("url(#") and value.endswith(")"):
            return value[5:-1]  # Remove 'url(#' and ')'
        return None

    def get_element_info(element):
        """Get common element information"""
        return {
            "element_tag": clean_tag_name(element),
            "element_id": element.get("id"),
            "element_title": find_element_title(element),
            "element": element,
        }

    # 1. Extract <use> elements (symbol usage)
    use_elements = tree.xpath("//svg:use", namespaces=namespaces) + tree.xpath("//use")

    for use_elem in use_elements:
        # Try both href and xlink:href
        href = (
            use_elem.get("href")
            or use_elem.get("{http://www.w3.org/1999/xlink}href")
            or use_elem.get("xlink:href")
        )

        if href and href.startswith("#"):
            usage_data["symbol_uses"].append(
                {
                    "ref": href[1:],  # Remove the '#'
                    "x": use_elem.get("x", "0"),
                    "y": use_elem.get("y", "0"),
                    "width": use_elem.get("width"),
                    "height": use_elem.get("height"),
                    "transform": use_elem.get("transform"),
                    "class": use_elem.get("class"),
                    "style": use_elem.get("style"),
                    **get_element_info(use_elem),
                }
            )

    # 2. Extract fill references (with better namespace handling)
    fill_queries = [
        ("//*[@fill]", None, "All elements with fill attr"),
        ("//svg:*[@fill]", namespaces, "SVG namespaced elements with fill attr"),
        ('//*[contains(@style, "fill")]', None, 'Elements with "fill" in style'),
    ]
    fill_elements = sum([tree.xpath(q, namespaces=n) for q, n, d in fill_queries], [])
    # Remove duplicates:
    unique_fill_elements = list({id(elem): elem for elem in fill_elements}.values())

    for elem in unique_fill_elements:
        fill_value = extract_attr_or_style_value(elem, "fill")
        ref = extract_url_ref(fill_value)
        if ref:
            usage_data["fill_refs"].append(
                {"ref": ref, "fill_value": fill_value, **get_element_info(elem)}
            )

    # 3. Extract stroke references (with better namespace handling)
    stroke_queries = [
        ("//*[@stroke]", None, "All elements with stroke attr"),
        ("//svg:*[@stroke]", namespaces, "SVG namespaced elements with stroke attr"),
        ('//*[contains(@style, "stroke")]', None, 'Elements with "stroke" in style'),
    ]
    stroke_elements = sum(
        [tree.xpath(q, namespaces=n) for q, n, d in stroke_queries], []
    )
    # Remove duplicates:
    unique_stroke_elements = list({id(elem): elem for elem in stroke_elements}.values())

    for elem in unique_stroke_elements:
        stroke_value = elem.get("stroke", "")
        strok_value = extract_attr_or_style_value(elem, "stroke")
        ref = extract_url_ref(stroke_value)
        if ref:
            usage_data["stroke_refs"].append(
                {"ref": ref, "stroke_value": stroke_value, **get_element_info(elem)}
            )

    # 4. Extract clip-path references
    clip_elements = tree.xpath("//*[@clip-path]")
    for elem in clip_elements:
        # clip_value = elem.get("clip-path", "")
        clip_value = extract_attr_or_style_value(elem, "clip-path")
        ref = extract_url_ref(clip_value)
        if ref:
            usage_data["clip_path_refs"].append(
                {"ref": ref, "clip_path_value": clip_value, **get_element_info(elem)}
            )

    # 5. Extract mask references
    mask_elements = tree.xpath("//*[@mask]")
    for elem in mask_elements:
        mask_value = elem.get("mask", "")
        mask_value = extract_attr_or_style_value(elem, "mask")
        ref = extract_url_ref(mask_value)
        if ref:
            usage_data["mask_refs"].append(
                {"ref": ref, "mask_value": mask_value, **get_element_info(elem)}
            )

    # 6. Extract marker references (marker-start, marker-mid, marker-end)
    marker_attributes = ["marker-start", "marker-mid", "marker-end"]
    for marker_attr in marker_attributes:
        marker_elements = tree.xpath(f"//*[@{marker_attr}]")
        for elem in marker_elements:
            # marker_value = elem.get(marker_attr, "")
            marker_value = extract_attr_or_style_value(elem, marker_attr)
            ref = extract_url_ref(marker_value)
            if ref:
                usage_data["marker_refs"].append(
                    {
                        "ref": ref,
                        "marker_type": marker_attr,
                        "marker_value": marker_value,
                        **get_element_info(elem),
                    }
                )

    # 7. Extract filter references
    filter_elements = tree.xpath("//*[@filter]")
    for elem in filter_elements:
        # filter_value = elem.get("filter", "")
        filter_value = extract_attr_or_style_value(elem, "filter")
        ref = extract_url_ref(filter_value)
        if ref:
            usage_data["filter_refs"].append(
                {"ref": ref, "filter_value": filter_value, **get_element_info(elem)}
            )

    if 0:  # TODO: do we need this?
        # 8. Categorize fill/stroke refs by type (gradients vs patterns)
        # Move gradient refs to separate category if needed
        for fill_ref in usage_data["fill_refs"][
            :
        ]:  # Copy list to modify during iteration
            # This could be enhanced to actually check what the ref points to
            pass

        for stroke_ref in usage_data["stroke_refs"][:]:
            # This could be enhanced to actually check what the ref points to
            pass

    # We don't need this anymore:
    # # 9. Extract other URL references from style attributes
    # style_elements = tree.xpath("//*[@style]")
    # for elem in style_elements:
    #     style_value = elem.get("style", "")
    #     # Simple regex-like extraction for url() in styles
    #     import re

    #     url_matches = re.findall(r"url\(#([^)]+)\)", style_value)
    #     for ref in url_matches:
    #         usage_data["other_refs"].append(
    #             {
    #                 "ref": ref,
    #                 "attribute": "style",
    #                 "style_value": style_value,
    #                 **get_element_info(elem),
    #             }
    #         )

    return usage_data


def print_usage_summary(usage_data: Dict) -> None:
    """
    Print a summary of extracted usages.

    Args:
        usage_data: The result from extract_svg_usages()
    """
    print("SVG Usage Summary:")
    print("=" * 40)

    for category, items in usage_data.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        for item in items:
            ref_str = f"#{item['ref']} ({item['element_title']}) - "
            element_info = f" in <{item['element_tag']}>"
            if item.get("element_id"):
                element_info += f" (id: {item['element_id']})"

            if category == "symbol_uses":
                pos_info = f" at ({item['x']}, {item['y']})"
                print(f"  - {ref_str}{pos_info}{element_info}")
            elif category == "marker_refs":
                marker_type = item.get("marker_type", "marker")
                print(f"  - {ref_str} as {marker_type}{element_info}")
            else:
                print(f"  - {ref_str}{element_info}")


def get_all_referenced_ids(usage_data: Dict) -> set:
    """
    Get a set of all referenced IDs from the usage data.

    Args:
        usage_data: The result from extract_svg_usages()

    Returns:
        Set of all referenced ID strings
    """
    referenced_ids = set()

    for category, items in usage_data.items():
        for item in items:
            if "ref" in item:
                referenced_ids.add(item["ref"])

    return referenced_ids
