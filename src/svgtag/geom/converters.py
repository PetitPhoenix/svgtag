"""Conversions entre Shapely, SVG et mesh"""
import os
import re
import tempfile

from ..svg.base import SVG
from .operations import resolve_polygons

# Rotation angles are divided by this factor before trimesh reads the SVG.
TRIMESH_ANGLE_FACTOR = -3300


def to_svg_path(polygon):
    """Convertit un Polygon Shapely en path SVG avec trous"""
    path_d = ""
    
    # Extérieur (sens horaire)
    coords = list(polygon.exterior.coords)
    if coords:
        path_d += f"M {coords[0][0]:.3f} {coords[0][1]:.3f} "
        for x, y in coords[1:-1]:
            path_d += f"L {x:.3f} {y:.3f} "
        path_d += "Z "
    
    # Trous (sens anti-horaire pour SVG)
    for interior in polygon.interiors:
        coords = list(interior.coords)
        if coords:
            path_d += f"M {coords[0][0]:.3f} {coords[0][1]:.3f} "
            for x, y in coords[1:-1]:
                path_d += f"L {x:.3f} {y:.3f} "
            path_d += "Z "
    
    return path_d.strip()


def to_svg(geometry, width=None, height=None):
    """
    Convertit une géométrie Shapely en objet SVG
    
    Args:
        geometry: Polygon Shapely
        width, height: Dimensions du SVG (auto si None)
    
    Returns:
        SVG object
    """
    # Calculer les dimensions si non fournies
    if width is None or height is None:
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
    
    svg = SVG()
    svg.width = width
    svg.height = height
    svg.viewBox = [0, 0, width, height]
    svg.unit = "mm"
    
    path_d = to_svg_path(geometry)
    svg.add_element('path', {
        'd': path_d,
        'fill': 'none',
        'stroke': 'black',
        'stroke-width': 0.1
    })
    svg.update_svg_content()
    
    return svg


def prepare_for_trimesh_angles(svg):
    """
    Prepare SVG for trimesh by converting rotation angles.

    Args:
        svg: SVG object

    Returns:
        New SVG object with converted angles
    """
    # Update content first
    svg.update_svg_content()
    svg_content = svg.content

    # Convert rotation angles in content
    def convert_rotation(match):
        angle = float(match.group(1))
        cx = match.group(2)
        cy = match.group(3)

        trimesh_angle = angle / TRIMESH_ANGLE_FACTOR
        return f'rotate({trimesh_angle} {cx} {cy})'

    converted_count = len(re.findall(r'rotate\(([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', svg_content))

    svg_content = re.sub(
        r'rotate\(([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)',
        convert_rotation,
        svg_content
    )

    if converted_count > 0:
        print(f"  Converted {converted_count} rotation(s) for trimesh")

    # Create new SVG and preserve structure
    new_svg = SVG()
    new_svg.width = svg.width
    new_svg.height = svg.height
    new_svg.viewBox = svg.viewBox.copy() if svg.viewBox else None
    new_svg.unit = svg.unit

    # IMPORTANT: Copy elements structure (preserves matrix transforms like flip)
    new_svg.elements = [elem.copy() if isinstance(elem, dict) else elem for elem in svg.elements]

    # Now convert rotation angles in elements
    def convert_element_rotations(element):
        """Recursively convert rotation angles in elements."""
        if isinstance(element, dict):
            # Convert rotation if present
            if element.get('rotation') is not None:
                element['rotation'] = element['rotation'] / TRIMESH_ANGLE_FACTOR

            # Recurse into group elements
            if element.get('tag') == 'g' and element.get('elements'):
                for child in element['elements']:
                    convert_element_rotations(child)

    for element in new_svg.elements:
        convert_element_rotations(element)

    # Update content with converted elements
    new_svg.update_svg_content()

    return new_svg


def svg_to_path2d(svg, prepare=True):
    """Convert SVG object to trimesh Path2D."""
    import trimesh
    if prepare:
        svg = prepare_for_trimesh_angles(svg)

    svg.update_svg_content()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8') as tmp:
        tmp.write(svg.content)
        tmp_path = tmp.name

    with open(tmp_path, 'rb') as f:
        path2d = trimesh.load_path(f, file_type='svg')

    os.unlink(tmp_path)
    return path2d


def glyph_polygons(text_svg):
    """Polygons of a text SVG, counters correctly nested as holes.

    Uses resolve_polygons (containment-based nesting) rather than
    Path2D.polygons_full, which misses counters for some fonts (e.g. Inter):
    the 'e'/'a'/'o' counters would otherwise come out filled when thickened.
    """
    return resolve_polygons(list(svg_to_path2d(text_svg).polygons_closed))
