"""
Test de calibration : compare plusieurs tolerances de simplify()
pour Astral Sisters (police complexe).

À placer dans scripts/test_simplify.py et lancer depuis la racine.
Génère des HTML 3D + SVG pour comparaison visuelle.
"""
import sys
from pathlib import Path
import time
import logging

logging.getLogger('fontTools').setLevel(logging.ERROR)

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone
from svgtag.svg.base import SVG
from svgtag.mesh.extrusion import svg_to_path2d


# Configuration test
FONT_PATH = str(PROJECT_ROOT / "static" / "fonts" / "AstralSisters" / "Astral Sisters.ttf")
TEST_TEXT = "Bienvenue Profitez du Wifi"

shape_svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)
main_area = layout.get_area('main')

recto_svg = SVG()
recto_svg.width = shape_svg.width
recto_svg.height = shape_svg.height
recto_svg.viewBox = shape_svg.viewBox.copy()
recto_svg.unit = "mm"
add_text_zone(recto_svg, TEST_TEXT, FONT_PATH, main_area)
recto_svg.update_svg_content()

path2d = svg_to_path2d(recto_svg)
polygons = path2d.polygons_full

print(f"Polygons: {len(polygons)}\n")
print(f"{'#':<4} {'AREA':<10} {'HOLES':<6} {'BBOX W':<8} {'BBOX H':<8} {'IS_VOL':<8} {'WATER':<8} {'NOTES'}")
print("-" * 100)

for i, poly in enumerate(polygons):
    bbox = poly.bounds
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    n_holes = len(poly.interiors)
    
    # Try to extrude this single polygon
    try:
        mesh = trimesh.creation.extrude_polygon(poly, height=1)
        is_vol = mesh.is_volume
        is_wat = mesh.is_watertight
        n_verts = len(mesh.vertices)
    except Exception as e:
        is_vol = False
        is_wat = False
        n_verts = 0
    
    status = "✓" if is_vol else "✗"
    notes = ""
    if poly.area < 0.01:
        notes = "DEGENERATE (area~0)"
    elif width < 0.05 or height < 0.05:
        notes = "VERY THIN"
    
    print(f"{i:<4} {poly.area:<10.3f} {n_holes:<6} {width:<8.2f} {height:<8.2f} "
          f"{str(is_vol):<8} {str(is_wat):<8} {status} {notes}")
