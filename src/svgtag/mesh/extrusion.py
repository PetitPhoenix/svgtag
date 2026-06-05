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

def _resolve_polygons(closed_polygons):
    """Build properly nested + non-overlapping polygons.

    Iteratively, for each polygon (largest first):
    - Smaller polygons strictly contained → absorbed as holes (counters)
    - Smaller polygons that overlap (intersect but not contained) → unioned
      with parent (e.g. f bar+stem, cursive ligatures)
    - Disjoint polygons → left as separate parents in next iterations
    """
    polys = sorted(closed_polygons, key=lambda p: p.area, reverse=True)
    used = [False] * len(polys)
    result = []
    for i in range(len(polys)):
        if used[i]:
            continue
        used[i] = True
        parent = polys[i]
        absorbed_holes = []
        # Loop until no more absorptions/unions (parent may grow via union
        # and then absorb new neighbors)
        changed = True
        while changed:
            changed = False
            for j in range(len(polys)):
                if used[j] or j == i:
                    continue
                child = polys[j]
                if parent.contains(child):
                    absorbed_holes.append(list(child.exterior.coords))
                    used[j] = True
                    changed = True
                elif parent.overlaps(child):
                    parent = parent.union(child)
                    used[j] = True
                    changed = True
        # Build final polygon (union may have produced MultiPolygon - rare)
        if isinstance(parent, ShapelyPolygon):
            all_holes = ([list(r.coords) for r in parent.interiors]
                         + absorbed_holes)
            result.append(ShapelyPolygon(parent.exterior.coords, holes=all_holes))
        else:
            for p in parent.geoms:
                result.append(p)
    return result


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
      2. _resolve_polygons → nest holes (counters strictly contained) and
         union genuinely-overlapping polygons (e.g. f bar+stem, cursive
         ligatures), while leaving touching neighbours alone (e.g. QR
         modules sharing an edge)
      3. extrude each resolved polygon individually
      4. concatenate (no trimesh.boolean.union: meshes are disjoint by
         construction and boolean.union can silently collapse holes)
    """
    polygons = _resolve_polygons(list(path2d.polygons_closed))
    
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


# ============================================================================
# Glyph thickening (laser / 3D-print legibility)
# ============================================================================
# Thicken text *geometry* (Shapely buffer) so thin strokes — especially cursive
# ones — reach a printable minimum width, without changing the font. The 2D
# counterpart (drawing thickened glyphs into an SVG) lives in svg.text
# (add_thickened_text), which reuses glyph_polygons / thicken_polygons below.

def glyph_polygons(text_svg):
    """Polygons of a text SVG, counters correctly nested as holes.

    Uses _resolve_polygons (containment-based nesting) rather than
    Path2D.polygons_full, which misses counters for some fonts (e.g. Inter):
    the 'e'/'a'/'o' counters would otherwise come out filled when thickened.
    """
    return _resolve_polygons(list(svg_to_path2d(text_svg).polygons_closed))


def thicken_polygons(polygons, offset, join_style=1):
    """Thicken polygons by ``offset`` per side (round buffer + clean union).

    ``unary_union`` is essential: without it, overlapping cursive glyphs fill a
    neighbour's counter (overlapping-fills artifact). ``orient`` enforces
    exterior-CCW / holes-CW so the result renders under any fill-rule and
    extrudes watertight. ``offset <= 0`` returns the polygons unchanged.
    """
    from shapely.geometry import MultiPolygon
    from shapely.ops import unary_union
    if not offset or offset <= 0:
        return [p for p in polygons if not p.is_empty and p.area > 1e-9]
    buffered = [p.buffer(offset, join_style=join_style)
                for p in polygons if not p.is_empty]
    if not buffered:
        return []
    merged = unary_union(buffered)
    geoms = merged.geoms if isinstance(merged, MultiPolygon) else [merged]
    return [orient(g, sign=1.0) for g in geoms if g.area > 1e-9]


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