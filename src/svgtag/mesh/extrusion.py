"""SVG to 3D mesh extrusion utilities"""
import logging

import trimesh
from shapely.geometry.polygon import orient

from ..geom.converters import glyph_polygons
from ..geom.operations import resolve_polygons, thicken_polygons


logger = logging.getLogger(__name__)

# Minimum polygon area (mm²) — below this, polygon is considered degenerate
MIN_POLYGON_AREA = 0.01

# Simplification tolerance (mm) — removes redundant points that cause
# numerical degeneracies in trimesh's triangulation. 0.001mm is invisible
# but enough to clean up dense Bezier-derived polygons (e.g. complex script fonts).
SIMPLIFY_TOLERANCE = 0.001

def _extrude_polygon(polygon, thickness):
    """Extrude a single Shapely polygon (with optional holes) into a
    watertight mesh. Simplify removes Bezier tessellation noise; orient
    enforces Shapely's exterior-CCW + holes-CW convention required by
    trimesh's triangulator."""
    polygon = polygon.simplify(SIMPLIFY_TOLERANCE)
    polygon = orient(polygon, sign=1.0)
    mesh = trimesh.creation.extrude_polygon(polygon, height=thickness)
    # Thin/tiny glyphs (punctuation in a fine font) can yield a few degenerate
    # (zero-area) faces -> the mesh is no longer watertight, and concatenations
    # / downstream boolean engraving silently skip it. Drop degenerate faces and
    # weld vertices (no fill_holes -> glyph counters preserved).
    if not mesh.is_watertight:
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.merge_vertices()
    return mesh


def extrude_path(path2d, thickness):
    """Extrude a 2D path into a single 3D Trimesh (or None).

    Pipeline:
      1. polygons_closed → flat list of Shapely polygons
      2. resolve_polygons → nest holes (counters strictly contained) and
         union genuinely-overlapping polygons (e.g. f bar+stem, cursive
         ligatures), while leaving touching neighbours alone (e.g. QR
         modules sharing an edge)
      3. extrude each resolved polygon individually
      4. concatenate (no trimesh.boolean.union: meshes are disjoint by
         construction and boolean.union can silently collapse holes)
    """
    polygons = resolve_polygons(list(path2d.polygons_closed))
    
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
            logger.warning("skipped polygon (area=%.3f): %s", poly.area, e)
            skipped += 1

    if skipped:
        logger.info("extrude_path: skipped %d degenerate polygon(s)", skipped)

    if not meshes:
        return None
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.util.concatenate(meshes)


def extrude_text(text_svg, thickness, offset=0.0):
    """Watertight 3D mesh of the (optionally thickened) text. ``None`` if empty.

    Extruded polygon-by-polygon (``_extrude_polygon``) so it is watertight by
    construction — counters stay holes, never filled.
    """
    polys = glyph_polygons(text_svg)
    if offset and offset > 0:
        polys = thicken_polygons(polys, offset)
    meshes = []
    for g in polys:
        if g.area <= 1e-9:
            continue
        try:
            meshes.append(_extrude_polygon(g, thickness))
        except Exception:
            pass
    if not meshes:
        return None
    return meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)