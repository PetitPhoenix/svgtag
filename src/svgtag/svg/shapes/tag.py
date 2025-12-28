"""Tag SVG generators with printable areas"""
from ...geom import tag_circle, tag_rectangle, tag_triangle, to_svg_path, add_hole
from ..base import SVG
from ..layouts import tag_layout


def _create_tag_svg(geom, length, height, has_ear, border):
    """
    Create SVG from tag geometry.
    Uses geometry bounds for viewBox.
    """
    # Get bounds from geometry
    bounds = geom.bounds
    minx, miny, maxx, maxy = bounds
    
    # Create SVG
    svg = SVG()
    svg.width = maxx - minx
    svg.height = maxy - miny
    svg.viewBox = [minx, miny, maxx - minx, maxy - miny]
    svg.unit = "mm"
    
    # Add path
    path_d = to_svg_path(geom)
    svg.add_element('path', {
        'd': path_d,
        'fill': 'none',
        'stroke': 'black',
        'stroke-width': 0.1
    })
    svg.update_svg_content()
    
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