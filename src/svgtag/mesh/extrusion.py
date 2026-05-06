"""SVG to 3D mesh extrusion utilities"""
import os
import trimesh
import tempfile
from shapely.geometry.polygon import orient
from shapely.geometry import Polygon as ShapelyPolygon
from .svg_helpers import prepare_for_trimesh_angles


# Minimum polygon area (mm²) — below this, polygon is considered degenerate
MIN_POLYGON_AREA = 0.01

# Simplification tolerance (mm) — removes redundant points that cause
# numerical degeneracies in trimesh's triangulation. 0.001mm is invisible
# but enough to clean up dense Bezier-derived polygons (e.g. complex script fonts).
SIMPLIFY_TOLERANCE = 0.001


def _augment_orphan_holes(closed_polygons):
    """Take polygons_closed (which already nests holes when winding is
    consistent) and absorb any smaller polygon strictly contained inside
    a larger one as an additional hole. Handles cases where SVG/font
    contour winding is inconsistent (e.g. Inter's 'B' counters)."""
    polys = sorted(closed_polygons, key=lambda p: p.area, reverse=True)
    used = [False] * len(polys)
    result = []
    for i, parent in enumerate(polys):
        if used[i]:
            continue
        used[i] = True
        holes = [list(r.coords) for r in parent.interiors]
        for j in range(i + 1, len(polys)):
            if used[j]:
                continue
            if parent.contains(polys[j].representative_point()):
                holes.append(list(polys[j].exterior.coords))
                used[j] = True
        result.append(ShapelyPolygon(parent.exterior.coords, holes=holes))
    return result


def _extrude_polygon(polygon, thickness):
    """Extrude a single Shapely polygon (with optional holes) into a
    watertight mesh. Simplify removes Bezier tessellation noise; orient
    enforces Shapely's exterior-CCW + holes-CW convention required by
    trimesh's triangulator."""
    polygon = polygon.simplify(SIMPLIFY_TOLERANCE)
    polygon = orient(polygon, sign=1.0)
    return trimesh.creation.extrude_polygon(polygon, height=thickness)


def extrude_path(path2d, thickness):
    """Extrude a 2D path into a single 3D Trimesh (or None).

    Pipeline:
      1. polygons_closed → Shapely's already-nested polygons
      2. _augment_orphan_holes → absorb separately-listed inner contours
         when font winding is inconsistent
      3. extrude each polygon individually
      4. concatenate (no boolean union: meshes are guaranteed disjoint
         by step 2, and trimesh.boolean.union can silently collapse holes
         depending on the backend)
    """
    polygons = _augment_orphan_holes(list(path2d.polygons_closed))

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
    return trimesh.util.concatenate(meshes)


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