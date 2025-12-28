"""Composition utilities for SVG text zones"""
from .text import text_svg
from .layout import PrintableArea


def add_text_zone(svg, text, font_path, zone, rotation=0, interline_ratio=0.8, outline=False, n=None, text_scale=1.0):
    """
    Add text to a zone with optional rotation and scaling.
    
    Args:
        svg: SVG object to add text to
        text: Text content (supports \n for manual line breaks)
        font_path: Path to TTF font file
        zone: PrintableArea or tuple (x, y, width, height)
        rotation: Rotation angle in degrees (overridden by zone.rotation if present)
        interline_ratio: Line spacing ratio
        outline: Whether to add debug outline
        n: Number of lines (None = auto, integer = force)
        text_scale: Scale factor for text size (0.5 = 50%, 1.0 = 100%, 2.0 = 200%)
    """
    if isinstance(zone, PrintableArea):
        x, y, w, h = zone.x, zone.y, zone.width, zone.height
        rotation = zone.rotation if zone.rotation else rotation
    else:
        x, y, w, h = zone
    
    # Swap width/height for 90°/270° rotations
    if rotation in [90, -90, 270]:
        text_width = h
        text_height = w
    else:
        text_width = w
        text_height = h
    
    # Apply text_scale to zone dimensions
    scaled_width = text_width * text_scale
    scaled_height = text_height * text_scale
    
    # Center scaled text in original zone
    render_x = x + (w - scaled_width) / 2
    render_y = y + (h - scaled_height) / 2
    
    # Generate text SVG
    svg_text = text_svg(
        text=text,
        font_path=font_path,
        font_size=None,
        zone_width=scaled_width,
        zone_height=scaled_height,
        x0=render_x,
        y0=render_y,
        interline_ratio=interline_ratio,
        n=n
    )
    
    # Apply rotation with group transform (clean and proper)
    if rotation != 0:
        cx = x + w / 2
        cy = y + h / 2
        
        # Add elements in a group with rotation
        svg.add_group(
            svg_text.elements,
            translate=None,
            scale=None,
            rotation=rotation,
            rotation_center=[cx, cy]
        )
    else:
        svg.add_svg(svg_text)
    
    if outline:
        add_outline(svg, (x, y, w, h), color="red")


def add_outline(svg, zone, color="red", stroke_width=0.2):
    """Add debug rectangle outline"""
    if isinstance(zone, PrintableArea):
        x, y, w, h = zone.x, zone.y, zone.width, zone.height
    else:
        x, y, w, h = zone
    
    svg.add_element('rect', {
        'x': x,
        'y': y,
        'width': w,
        'height': h,
        'stroke': color,
        'fill': 'none',
        'stroke-width': stroke_width
    })


def add_border_outline(svg, zone, border, color="blue", stroke_width=0.2):
    """
    Add debug outline with border offset (expands outside the zone).
    
    Args:
        svg: SVG object
        zone: PrintableArea or (x, y, w, h) tuple
        border: Border width in mm (positive = expands outward)
        color: Stroke color
        stroke_width: Line width
    """
    if isinstance(zone, PrintableArea):
        x, y, w, h = zone.x, zone.y, zone.width, zone.height
    else:
        x, y, w, h = zone
    
    svg.add_element('rect', {
        'x': x - border,
        'y': y - border,
        'width': w + 2 * border,
        'height': h + 2 * border,
        'stroke': color,
        'fill': 'none',
        'stroke-width': stroke_width
    })