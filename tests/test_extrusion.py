import io
from collections import Counter
from types import SimpleNamespace

import numpy as np
import trimesh
from shapely.geometry import Polygon, box

from svgtag.mesh import extrusion as ex


def _stl_reloaded(mesh):
    buf = io.BytesIO()
    mesh.export(buf, file_type='stl')
    buf.seek(0)
    return trimesh.load(buf, file_type='stl')


def _edges_shared_by_more_than_two_faces(mesh):
    mesh = mesh.copy()
    mesh.merge_vertices()
    return sum(1 for n in Counter(map(tuple, np.sort(mesh.edges, axis=1))).values() if n > 2)


def test_contour_trimesh_could_not_build_is_ignored():
    path = SimpleNamespace(polygons_closed=[box(0, 0, 10, 10), None])
    assert ex.extrude_path(path, 1.0).volume == 100


def test_squares_touching_by_edge_or_corner_give_manifold_stl():
    squares = [box(x, y, x + 1, y + 1) for x, y in [(0, 0), (1, 0), (1, 1), (3, 3), (2, 2)]]
    path = SimpleNamespace(polygons_closed=squares)
    stl = _stl_reloaded(ex.extrude_path(path, 1.0))
    assert _edges_shared_by_more_than_two_faces(stl) == 0
    assert stl.is_volume


def test_vertices_merged_by_float32_give_manifold_stl():
    outer = [(100, 100), (105, 100), (110, 99), (110, 110), (100, 110)]
    hole = [(105, 100 + 1e-8), (107, 103), (103, 103)]
    path = SimpleNamespace(polygons_closed=[Polygon(outer), Polygon(hole)])
    stl = _stl_reloaded(ex.extrude_path(path, 1.0))
    assert _edges_shared_by_more_than_two_faces(stl) == 0
    assert stl.is_volume
