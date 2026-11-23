"""Tag SVG generators with printable areas"""
from ...geom import tag_circle, tag_rectangle, tag_triangle, to_svg, add_hole
from ..layouts import tag_layout


def _create_tag_svg(geom, length, height, has_ear, border):
    """
    Create SVG from tag geometry.
    Uses geometry bounds for viewBox.
    """
    svg = to_svg(geom)
    minx, miny = svg.viewBox[0], svg.viewBox[1]

    # Create layout
    layout = tag_layout(length, height, has_ear=has_ear, border=border, 
                       viewbox_minx=minx, viewbox_miny=miny)
    
    return svg, layout


def tag_circle_svg(length=80, height=35, hole_diameter=6, border=3):
    """Create a circular tag SVG."""
    geom = tag_circle(length, height)
    
    has_ear = hole_diameter > 0
    if has_ear:
        hole_x = -height / 2 + height / 4
        hole_y = height / 2
        geom = add_hole(geom, hole_diameter, hole_x, hole_y)
    
    return _create_tag_svg(geom, length, height, has_ear, border)


def tag_rectangle_svg(length=80, height=35, hole_diameter=6, border=3, corner_radius=3):
    """Create a rectangular tag SVG."""
    has_ear = hole_diameter > 0
    
    if has_ear:
        geom = tag_rectangle(length + height / 2, height, corner_radius)
        hole_x = height / 4
        hole_y = height / 2
        geom = add_hole(geom, hole_diameter, hole_x, hole_y)
    else:
        geom = tag_rectangle(length, height, corner_radius)
    
    return _create_tag_svg(geom, length, height, has_ear, border)


def tag_triangle_svg(length=80, height=35, hole_diameter=6, border=3):
    """Create a triangular tag SVG."""
    geom = tag_triangle(length, height)
    
    has_ear = hole_diameter > 0
    if has_ear:
        hole_x = -hole_diameter / 2
        hole_y = height / 2
        geom = add_hole(geom, hole_diameter, hole_x, hole_y)
    
    return _create_tag_svg(geom, length, height, has_ear, border)