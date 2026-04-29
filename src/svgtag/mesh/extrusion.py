"""SVG to 3D mesh extrusion utilities"""
import os
import trimesh
import tempfile
from shapely.geometry.polygon import orient
from .svg_helpers import prepare_for_trimesh_angles


# Minimum polygon area (mm²) — below this, polygon is considered degenerate
MIN_POLYGON_AREA = 0.01

# Simplification tolerance (mm) — removes redundant points that cause
# numerical degeneracies in trimesh's triangulation. 0.001mm is invisible
# but enough to clean up dense Bezier-derived polygons (e.g. complex script fonts).
SIMPLIFY_TOLERANCE = 0.001


def _extrude_polygon(polygon, thickness):
    """
    Extrude a single Shapely polygon into a clean watertight mesh.
    
    Steps:
      1. Simplify to remove redundant points (Bezier tessellation often produces
         hundreds of points clustered within fractions of a millimeter)
      2. Orient CCW (Shapely standard) so trimesh produces correct normals
      3. Extrude
    """
    polygon = polygon.simplify(SIMPLIFY_TOLERANCE)
    polygon = orient(polygon, sign=1.0)
    return trimesh.creation.extrude_polygon(polygon, height=thickness)


def extrude_path(path2d, thickness):
    """
    Extrude a 2D path into a 3D mesh.

    Each Shapely polygon (with its holes) is extruded individually using
    trimesh.creation.extrude_polygon, after light simplification and CCW
    orientation to handle complex script fonts cleanly.

    Returns:
        trimesh.Trimesh OR list of trimesh.Trimesh
    """
    polygons = path2d.polygons_full

    if not polygons:
        return path2d.extrude(thickness)

    meshes = []
    skipped = 0
    for poly in polygons:
        if poly.area < MIN_POLYGON_AREA:
            skipped += 1
            continue
        try:
            meshes.append(_extrude_polygon(poly, thickness))
        except Exception as e:
            print(f"  Warning: skipped polygon (area={poly.area:.3f}): {e}")
            skipped += 1

    if skipped:
        print(f"  extrude_path: skipped {skipped} degenerate polygon(s)")

    if not meshes:
        return None

    if len(meshes) == 1:
        return meshes[0]

    # Try union for a clean single mesh
    try:
        unioned = trimesh.boolean.union(meshes)
        if unioned is not None and unioned.is_volume:
            return unioned
    except Exception:
        pass

    # Union failed → return list (assemble_plate handles iteration)
    return meshes


def svg_to_path2d(svg, prepare=True):
    """Convert SVG object to trimesh Path2D."""
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
