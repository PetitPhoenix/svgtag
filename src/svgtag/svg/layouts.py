"""Predefined layouts for common use cases"""
from .layout import Layout, PrintableArea  
from .text import get_text_dimensions


def tablet_simple_layout(width: float, height: float, padding: float = 3) -> Layout:
    """Simple tablet layout with one main text area."""
    layout = Layout(width, height, padding)
    layout.add_area('main', 0, 0, 1.0, 1.0, unit='ratio')
    return layout


def narcose_layout(
    width: float, 
    height: float, 
    padding: float = 3,
    title_ratio: float = 0.12,   # 12% pour le titre
    side_ratio: float = 0.12      # 12% pour le texte latéral
) -> Layout:
    """
    Narcose test plate layout with title, side text, and main text area.
    
    Layout structure:
    - Title: top strip (12% of height by default)
    - Side text: left column (12% of width by default)  
    - Main text: remaining area for numbers (bottom-right)
    - Main: full area (for brand positioning)
    
    Args:
        width: Total width in mm
        height: Total height in mm
        padding: Border padding in mm
        title_ratio: Title height as ratio of total height
        side_ratio: Side text width as ratio of total width
    
    Returns:
        Layout with 'title', 'side_text', 'main_text', 'main' areas
    """
    layout = Layout(width, height, padding)
    
    # Main = full area (for brand_layout calculations)
    layout.add_area('main', x=0, y=0, width=1.0, height=1.0, unit='ratio')
    
    # Title zone (top, full width)
    layout.add_area('title', x=side_ratio, y=0, width=1.0 - side_ratio, height=title_ratio, unit='ratio')
    
    # Side text zone (left column, below title)
    layout.add_area('side_text', x=0, y=title_ratio, width=side_ratio, height=1.0 - title_ratio, rotation=-90, unit='ratio')
    
    # Main text zone (numbers area - bottom-right, excluding title and side)
    layout.add_area('main_text', x=side_ratio, y=title_ratio, width=1.0 - side_ratio, height=1.0 - title_ratio, unit='ratio')
    
    return layout


def tag_layout(
    length: float,
    height: float,
    has_ear: bool = False,
    border: float = 3,
    viewbox_minx: float = 0,
    viewbox_miny: float = 0
) -> Layout:
    """
    Tag layout with main text area.
    
    Args:
        length: Tag length in mm (zone de texte uniquement)
        height: Tag height in mm
        has_ear: True si le tag a une oreille/zone pour trou à gauche
        border: Text border in mm
        viewbox_minx: ViewBox min X (pour coordonnées absolues)
        viewbox_miny: ViewBox min Y (pour coordonnées absolues)
    
    Returns:
        Layout with 'main' area
    """
    # Si ear, la zone de texte commence après l'espace de l'oreille
    if has_ear:
        total_width = length + height / 2
        layout = Layout(total_width, height, border)
        
        # Zone de texte : commence à viewbox_minx + height/2 (après l'oreille)
        text_x = viewbox_minx + height / 2 + border
        text_y = viewbox_miny + border
        text_width = length - 2 * border
        text_height = height - 2 * border
        
        layout.add_area('main', text_x, text_y, text_width, text_height, unit='mm')
    else:
        layout = Layout(length, height, border)
        text_x = viewbox_minx + border
        text_y = viewbox_miny + border
        text_width = length - 2 * border
        text_height = height - 2 * border
        
        layout.add_area('main', text_x, text_y, text_width, text_height, unit='mm')
    
    return layout

def brand_layout_auto(
    main_area: PrintableArea,
    text: str,
    font_path: str,
    brand_position: str = 'bottom-right',
    brand_width_scale: float = 0.35,
    border: float = 0,
    flip_axis: str = None,
    n: list = None
) -> tuple:
    """
    Create brand layout with auto-calculated dimensions based on actual text size.
    
    Args:
        main_area: Main printable area
        text: Brand text
        font_path: Font path
        brand_position: Position within main area
        brand_width_scale: Maximum width as fraction of main area width
        border: Border around brand
        flip_axis: Flip axis for verso positioning
        n: Line count override for text
    
    Returns:
        (Layout, text_width, text_height)
    """
    # Calculate max dimensions for text
    max_width = main_area.width * brand_width_scale
    max_height = main_area.height * brand_width_scale
    
    # Get actual text dimensions
    text_width, text_height = get_text_dimensions(text, font_path, max_width, max_height, n)
    
    # Adjust position if flip
    adjusted_position = brand_position
    if flip_axis:
        if flip_axis == 'horizontal':
            position_map = {
                'bottom-right': 'top-right',
                'bottom-left': 'top-left',
                'top-right': 'bottom-right',
                'top-left': 'bottom-left',
                'center': 'center'
            }
            adjusted_position = position_map.get(brand_position, brand_position)
        elif flip_axis == 'vertical':
            position_map = {
                'bottom-right': 'bottom-left',
                'bottom-left': 'bottom-right',
                'top-right': 'top-left',
                'top-left': 'top-right',
                'center': 'center'
            }
            adjusted_position = position_map.get(brand_position, brand_position)
    
    layout = Layout(main_area.width, main_area.height, border)
    
    # Calculate position based on actual text dimensions
    if adjusted_position == 'bottom-right':
        x = main_area.x + main_area.width - text_width - border
        y = main_area.y + main_area.height - text_height - border
    elif adjusted_position == 'bottom-left':
        x = main_area.x + border
        y = main_area.y + main_area.height - text_height - border
    elif adjusted_position == 'top-right':
        x = main_area.x + main_area.width - text_width - border
        y = main_area.y + border
    elif adjusted_position == 'top-left':
        x = main_area.x + border
        y = main_area.y + border
    elif adjusted_position == 'center':
        x = main_area.x + (main_area.width - text_width) / 2
        y = main_area.y + (main_area.height - text_height) / 2
    
    layout.add_area('brand', x, y, text_width, text_height, unit='mm')
    
    return layout, text_width, text_height


def brand_layout(
    main_area: PrintableArea,
    brand_position: str = 'bottom-right',
    brand_scale: float = 0.4,
    border: float = 3,
    flip_axis: str = None
) -> Layout:
    """
    Brand layout - small logo zone INSIDE a main area.
    
    Args:
        main_area: PrintableArea of the main zone (from tag or tablet layout)
        brand_position: Position within main area
        brand_scale: Scale factor relative to main area
        border: Border margin in mm
        flip_axis: 'horizontal' or 'vertical' if for verso
    
    Returns:
        Layout with 'brand' area
    """
    # Adjust position if flip
    if flip_axis:
        if flip_axis == 'horizontal':
            position_map = {
                'bottom-right': 'top-right',
                'bottom-left': 'top-left',
                'top-right': 'bottom-right',
                'top-left': 'bottom-left',
                'center': 'center'
            }
            brand_position = position_map.get(brand_position, brand_position)
        
        elif flip_axis == 'vertical':
            position_map = {
                'bottom-right': 'bottom-left',
                'bottom-left': 'bottom-right',
                'top-right': 'top-left',
                'top-left': 'top-right',
                'center': 'center'
            }
            brand_position = position_map.get(brand_position, brand_position)
    
    # Create layout based on main area dimensions
    layout = Layout(main_area.width, main_area.height, border)
    
    # Calculate brand dimensions (relative to main area)
    brand_width = main_area.width * brand_scale
    brand_height = main_area.height * brand_scale
    
    # Calculate position (relative to main area, then offset by main_area position)
    if brand_position == 'bottom-right':
        x = main_area.x + main_area.width - brand_width - border
        y = main_area.y + main_area.height - brand_height - border
    elif brand_position == 'bottom-left':
        x = main_area.x + border
        y = main_area.y + main_area.height - brand_height - border
    elif brand_position == 'top-right':
        x = main_area.x + main_area.width - brand_width - border
        y = main_area.y + border
    elif brand_position == 'top-left':
        x = main_area.x + border
        y = main_area.y + border
    elif brand_position == 'center':
        x = main_area.x + (main_area.width - brand_width) / 2
        y = main_area.y + (main_area.height - brand_height) / 2
    
    layout.add_area('brand', x, y, brand_width, brand_height, unit='mm')
    
    return layout


def wifi_qr_layout(width, height, padding=5):
    """
    WiFi QR code card layout with text fields and QR zone.
    
    Args:
        width: Card width in mm
        height: Card height in mm
        padding: Edge padding in mm
    
    Returns:
        Layout with defined areas
    """
    layout = Layout(width, height, padding)
    
    # Text areas (left 2/3)
    layout.add_area('title', 0, 0, 2/3, 1/4, unit='ratio')
    layout.add_area('subtitle', 0, 1/4, 2/3, 1/10, unit='ratio')
    layout.add_area('network_label', 0, 6/12, 1/2, 1/10, unit='ratio')
    layout.add_area('network_value', 0, 7.2/12, 1/2, 1/12, unit='ratio')
    layout.add_area('password_label', 0, 9/12, 1/2, 1/10, unit='ratio')
    layout.add_area('password_value', 0, 10.2/12, 1/2, 1/12, unit='ratio')
    
    # QR code (right side)
    layout.add_area('qr_code', 3/5, 1/2, 2/5, 1/2, unit='ratio')

    # Signal icon (top right)
    layout.add_area('signal_icon', 2/3, 1/8, 1/3, 1/4, unit='ratio')

    return layout


def business_card_layout(width, height, padding=5):
    """
    Landscape business-card QR layout (e.g. 85×55 mm vCard).

    Unlike :func:`wifi_qr_layout` (tuned for a square card), this spreads the
    text down a left column and gives the QR a large, vertically-centred block
    on the right with a caption zone under it — so a wide card doesn't cram all
    its text into the lower-left corner.

    Zones (ratios are relative to the padded inner box):
    - ``title``    : name, top of the left column (prominent)
    - ``org``      : company / role, under the name
    - ``line1..3`` : contact rows (phone / email / site), evenly spread
    - ``qr_code``  : large square QR, right side, vertically centred
    - ``qr_caption``: small strip under the QR (e.g. "Scan me")

    No ``signal_icon`` zone: the big QR carries the card on its own.

    Args:
        width: Card width in mm
        height: Card height in mm
        padding: Edge padding in mm

    Returns:
        Layout with defined areas
    """
    layout = Layout(width, height, padding)

    # Left text column (~56% of the inner width), spread over the full height.
    col_w = 0.56
    layout.add_area('title', 0, 0.06, col_w, 0.24, unit='ratio')   # name (script)
    layout.add_area('org',   0, 0.34, col_w, 0.12, unit='ratio')   # company/role
    layout.add_area('line1', 0, 0.51, col_w, 0.12, unit='ratio')   # contact rows,
    layout.add_area('line2', 0, 0.65, col_w, 0.12, unit='ratio')   #   evenly
    layout.add_area('line3', 0, 0.79, col_w, 0.12, unit='ratio')   #   spread

    # QR block (right side): large square, vertically centred, caption beneath.
    layout.add_area('qr_code',    0.62, 0.12, 0.38, 0.60, unit='ratio')
    layout.add_area('qr_caption', 0.60, 0.78, 0.42, 0.12, unit='ratio')

    return layout