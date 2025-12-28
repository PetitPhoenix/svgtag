"""Opérations booléennes 2D"""
from shapely.ops import unary_union as shapely_union
from shapely.geometry import MultiPolygon


def union(geometries):
    """Union de plusieurs géométries"""
    return shapely_union(geometries)


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