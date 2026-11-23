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
from .operations import (
    union, difference, buffer_geometry, validate,
    resolve_polygons, merge_touching, polygons_of, thicken_polygons, repair_variants,
)
from .converters import (
    to_svg_path, to_svg, prepare_for_trimesh_angles, svg_to_path2d, glyph_polygons,
)

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
    'resolve_polygons',
    'merge_touching',
    'polygons_of',
    'thicken_polygons',
    'repair_variants',
    # Converters
    'to_svg_path',
    'to_svg',
    'prepare_for_trimesh_angles',
    'svg_to_path2d',
    'glyph_polygons',
]