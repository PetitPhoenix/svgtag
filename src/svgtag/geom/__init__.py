"""Geometric primitives and operations (Shapely-based)."""
from .shapes import (
    rectangle,
    circle,
    rounded_rectangle,
    add_hole,
    tag_circle,
    tag_rectangle,
    tag_triangle,
    tablet_with_ear
)
from .operations import union, difference, buffer_geometry, validate
from .converters import to_svg_path, to_svg, to_mesh

__all__ = [
    # Shapes
    'rectangle',
    'circle',
    'rounded_rectangle',
    'add_hole',
    'tag_circle',
    'tag_rectangle',
    'tag_triangle',
    'tablet_with_ear',
    # Operations
    'union',
    'difference',
    'buffer_geometry',
    'validate',
    # Converters
    'to_svg_path',
    'to_svg',
    'to_mesh',
]