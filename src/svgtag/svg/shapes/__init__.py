"""SVG shape generators."""
from .tag import tag_circle_svg, tag_rectangle_svg, tag_triangle_svg
from .tablet import tablet_svg
from .wifi import qr_code_svg, wifi_card_svg

__all__ = [
    'tag_circle_svg',
    'tag_rectangle_svg',
    'tag_triangle_svg',
    'tablet_svg',
    'qr_code_svg',
    'wifi_card_svg',
]