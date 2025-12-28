"""
Tag 3D recto uniquement
"""
from pathlib import Path
from trimesh import viewer
from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone
from svgtag.svg.base import SVG
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate, create_scene, export_stl

HERE = Path(__file__).resolve().parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

ROOT = HERE.parent
font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")

# 1. Créer la forme
shape_svg, _ = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)
shape_svg.generate_svg_file(str(output_path / "shape.svg"))

# 2. Créer le recto
_, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)
recto_svg = SVG()
recto_svg.width = shape_svg.width
recto_svg.height = shape_svg.height
recto_svg.viewBox = shape_svg.viewBox.copy()
recto_svg.unit = "mm"

area = layout.get_area('main')
add_text_zone(recto_svg, "Impression d'une étiquette", font_path, area)
recto_svg.update_svg_content()

# 3. Convertir en meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)

# 4. Assembler
plate = assemble_plate(shape_mesh, [recto_mesh])

# 5. Créer la scène
scene = create_scene([plate, recto_mesh])

# 6. Export
export_stl([plate, recto_mesh], str(output_path), ['mesh.stl', 'side_A.stl'])

with open(output_path / "tag_3D_recto.html", "w") as file:
    file.write(viewer.scene_to_html(scene))

print(f"✓ Tag 3D recto généré dans {output_path}")