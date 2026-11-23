"""SVG to 3D mesh extrusion utilities"""
import logging

import numpy as np
import trimesh
from shapely.geometry.polygon import orient

from ..geom.converters import glyph_polygons
from ..geom.operations import (
    merge_touching, polygons_of, repair_variants, resolve_polygons, thicken_polygons,
)


logger = logging.getLogger(__name__)

# Minimum polygon area (mm²) — below this, polygon is considered degenerate
MIN_POLYGON_AREA = 0.01

# Simplification tolerance (mm) — removes redundant points that cause
# numerical degeneracies in trimesh's triangulation. 0.001mm is invisible
# but enough to clean up dense Bezier-derived polygons (e.g. complex script fonts).
SIMPLIFY_TOLERANCE = 0.001

# Geometric tolerance (mm) of the extrusion: polygons closer than this are
# fused, details thinner than this may be removed.
TOLERANCE = 0.01


def _is_printable(mesh):
    """True if the mesh is a volume once its vertices are rounded to float32
    (the precision of STL)."""
    if mesh is None or not len(mesh.faces):
        return False
    v32 = np.asarray(mesh.vertices, dtype=np.float32).astype(np.float64)
    return trimesh.Trimesh(vertices=v32, faces=mesh.faces, process=True).is_volume


def _extrude_volume(polygon, thickness, tolerance):
    """Extrusions of the first variant of ``polygon`` (see
    geom.operations.repair_variants) whose meshes all pass ``_is_printable``.
    Empty list if none does."""
    for variant in repair_variants(polygon, tolerance):
        try:
            parts = [g for g in polygons_of(variant) if g.area >= MIN_POLYGON_AREA]
            meshes = [_extrude_polygon(g, thickness) for g in parts]
        except Exception:
            continue
        if meshes and all(_is_printable(m) for m in meshes):
            return meshes
    logger.warning("skipped non-printable polygon (area=%.3f)", polygon.area)
    return []


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


def extrude_path(path2d, thickness, tolerance=TOLERANCE):
    """Extrude a 2D path into a single 3D Trimesh (or None).

    Pipeline:
      1. polygons_closed → flat list of Shapely polygons
      2. resolve_polygons → nest holes (counters strictly contained) and
         union genuinely-overlapping polygons (e.g. f bar+stem, cursive
         ligatures)
      3. merge_touching → polygons closer than ``tolerance`` (e.g. QR
         modules sharing an edge or a corner) fused
      4. extrude each polygon individually (_extrude_volume)
      5. concatenate (no trimesh.boolean.union: meshes are disjoint by
         construction and boolean.union can silently collapse holes)
    """
    polygons = resolve_polygons(list(path2d.polygons_closed))

    if not polygons:
        return path2d.extrude(thickness)
    polygons = merge_touching(polygons, tolerance)

    meshes = []
    skipped = 0
    for poly in polygons:
        if poly.area < MIN_POLYGON_AREA:
            skipped += 1
            continue
        parts = _extrude_volume(poly, thickness, tolerance)
        if not parts:
            skipped += 1
        meshes.extend(parts)

    if skipped:
        logger.info("extrude_path: skipped %d degenerate polygon(s)", skipped)

    if not meshes:
        return None
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.util.concatenate(meshes)


def extrude_text(text_svg, thickness, offset=0.0, tolerance=TOLERANCE):
    """Watertight 3D mesh of the (optionally thickened) text. ``None`` if empty.

    Extruded polygon-by-polygon (``_extrude_polygon``) so it is watertight by
    construction — counters stay holes, never filled.
    """
    polys = glyph_polygons(text_svg)
    if offset and offset > 0:
        polys = thicken_polygons(polys, offset)
    meshes = []
    for g in merge_touching([g for g in polys if g.area > 1e-9], tolerance):
        meshes.extend(_extrude_volume(g, thickness, tolerance))
    if not meshes:
        return None
    return meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)
