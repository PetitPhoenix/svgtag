"""Tablet SVG generator with printable areas"""
from ...geom import tablet_with_ear, to_svg_path
from ..base import SVG
from ..layouts import tablet_simple_layout, narcose_layout


def tablet_svg(
    width: float = 80,
    height: float = 129,
    padding: float = 3,
    eyelet_outer_diameter: float = 18,
    eyelet_hole_diameter: float = 8,
    ear_offset: list = None,
    layout_type: str = 'simple',
    corner_radius: float = 3
):
    """
    Create a tablet SVG with defined printable areas.
    
    Args:
        width, height: Tablet dimensions in mm
        padding: Edge padding in mm
        eyelet_outer_diameter: Outer diameter of eyelet in mm
        eyelet_hole_diameter: Hole diameter in mm
        ear_offset: [x, y] position of ear center (None = top-left [5, 5])
        layout_type: 'simple', 'narcose', or custom Layout object
        corner_radius: Corner radius in mm
    
    Returns:
        (svg, layout): SVG object with shape, Layout object with printable areas
    
    Example:
        >>> svg, layout = tablet_svg(width=80, height=129, layout_type='narcose')
        >>> # svg contains the tablet shape
        >>> # layout.get_area('vertical_text') → PrintableArea for text
    """
    if ear_offset is None:
        ear_offset = [5, 5]
    
    # 1. Create geometry
    geom = tablet_with_ear(
        width=width,
        height=height,
        padding=corner_radius,
        eyelet_outer_diameter=eyelet_outer_diameter,
        eyelet_hole_diameter=eyelet_hole_diameter,
        ear_offset=ear_offset
    )
    
    # 2. Create SVG
    bounds = geom.bounds
    minx, miny, maxx, maxy = bounds
    svg_width = maxx - minx
    svg_height = maxy - miny
    
    svg = SVG()
    svg.width = svg_width
    svg.height = svg_height
    svg.viewBox = [minx, miny, svg_width, svg_height]
    svg.unit = "mm"
    
    # Add shape path
    path_d = to_svg_path(geom)
    svg.add_element('path', {
        'd': path_d,
        'fill': 'none',
        'stroke': 'black',
        'stroke-width': 0.1
    })
    svg.update_svg_content()
    
    # 3. Create layout
    if isinstance(layout_type, str):
        if layout_type == 'simple':
            layout = tablet_simple_layout(width, height, padding)
        elif layout_type == 'narcose':
            layout = narcose_layout(width, height, padding)
        else:
            raise ValueError(f"Unknown layout_type: {layout_type}")
    else:
        # Custom Layout object passed
        layout = layout_type
    
    return svg, layout