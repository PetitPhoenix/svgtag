"""Opérations 2D sur les géométries Shapely"""
from shapely import set_precision
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.strtree import STRtree


def union(geometries):
    """Union de plusieurs géométries"""
    return unary_union(geometries)


def difference(geom_a, geom_b):
    """Différence entre deux géométries"""
    return geom_a.difference(geom_b)


def buffer_geometry(geom, distance):
    """Buffer (offset) d'une géométrie"""
    return geom.buffer(distance)


def validate(geom):
    """Valide et répare une géométrie si nécessaire"""
    if not geom.is_valid:
        geom = geom.buffer(0)  # Trick pour réparer
    return geom


def resolve_polygons(closed_polygons):
    """Build properly nested + non-overlapping polygons.

    Iteratively, for each polygon (largest first):
    - Smaller polygons strictly contained → absorbed as holes (counters)
    - Smaller polygons that overlap (intersect but not contained) → unioned
      with parent (e.g. f bar+stem, cursive ligatures)
    - Disjoint polygons → left as separate parents in next iterations
    """
    polys = sorted((p for p in closed_polygons if p is not None),
                   key=lambda p: p.area, reverse=True)
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
        if isinstance(parent, Polygon):
            all_holes = ([list(r.coords) for r in parent.interiors]
                         + absorbed_holes)
            result.append(Polygon(parent.exterior.coords, holes=all_holes))
        else:
            for p in parent.geoms:
                result.append(p)
    return result


def merge_touching(polygons, tolerance):
    """Polygons closer than ``tolerance`` are fused (union, then closing of
    ``tolerance``). Without such a pair, the list is returned unchanged."""
    if len(polygons) < 2:
        return polygons
    tree = STRtree(polygons)
    touching = any(
        j > i and polygons[i].distance(polygons[j]) < tolerance
        for i, poly in enumerate(polygons)
        for j in tree.query(poly.buffer(tolerance))
    )
    if not touching:
        return polygons
    merged = unary_union(polygons).buffer(tolerance).buffer(-tolerance)
    return polygons_of(merged)


def polygons_of(geom):
    """Non-empty polygons of a Shapely geometry."""
    geoms = getattr(geom, 'geoms', [geom])
    return [g for g in geoms
            if isinstance(g, Polygon) and not g.is_empty and g.area > 1e-9]


def thicken_polygons(polygons, offset, join_style=1):
    """Thicken polygons by ``offset`` per side (round buffer + clean union).

    ``unary_union`` is essential: without it, overlapping cursive glyphs fill a
    neighbour's counter (overlapping-fills artifact). ``orient`` enforces
    exterior-CCW / holes-CW so the result renders under any fill-rule and
    extrudes watertight. ``offset <= 0`` returns the polygons unchanged.
    """
    if not offset or offset <= 0:
        return [p for p in polygons if not p.is_empty and p.area > 1e-9]
    buffered = [p.buffer(offset, join_style=join_style)
                for p in polygons if not p.is_empty]
    if not buffered:
        return []
    merged = unary_union(buffered)
    geoms = merged.geoms if isinstance(merged, MultiPolygon) else [merged]
    return [orient(g, sign=1.0) for g in geoms if g.area > 1e-9]


def repair_variants(polygon, tolerance):
    """Variants of ``polygon``, in order: as is; snapped to a grid of
    ``tolerance / 100``; closed by ``tolerance``; opened by ``tolerance / 2``;
    closed then opened. All but the first are snapped."""
    grid, close, opening = tolerance / 100, tolerance, tolerance / 2
    yield polygon
    yield set_precision(polygon, grid)
    closed = polygon.buffer(close).buffer(-close)
    yield set_precision(closed, grid)
    yield set_precision(polygon.buffer(-opening).buffer(opening), grid)
    yield set_precision(closed.buffer(-opening).buffer(opening), grid)
