"""SVG generation and composition module."""
from .base import SVG
from .text import text_svg
from .composition import add_text_zone, add_outline, add_border_outline
from .layout import Layout, PrintableArea
from .layouts import (
    tablet_simple_layout,
    narcose_layout,
    tag_layout,
    brand_layout,
    brand_layout_auto
)

__all__ = [
    'SVG',
    'text_svg',
    'add_text_zone',
    'add_outline',
    'add_border_outline',
    'Layout',
    'PrintableArea',
    'tablet_simple_layout',
    'narcose_layout',
    'tag_layout',
    'brand_layout',
    'brand_layout_auto',
]