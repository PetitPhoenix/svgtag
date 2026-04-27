"""
Exemple: Tag 3D recto-verso
Crée un tag 3D avec texte sur les deux faces
"""
from pathlib import Path
from trimesh import viewer
import trimesh
from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone
from svgtag.svg.base import SVG
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate, create_scene, export_stl, export_html

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")

# 1. Créer la forme
shape_svg, _ = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)

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

# 3. Créer le verso (flip vertical du texte)
verso_svg = SVG()
verso_svg.width = shape_svg.width
verso_svg.height = shape_svg.height
verso_svg.viewBox = shape_svg.viewBox.copy()
verso_svg.unit = "mm"

# Ajouter le texte
add_text_zone(verso_svg, "Recto / Verso", font_path, area, n=1)
verso_svg.update_svg_content()

# Flip le dernier élément (le texte) autour du centre de sa zone
center_x = area.x + area.width / 2
center_y = area.y + area.height / 2
# Type 1 de flip :
verso_svg_flipped = verso_svg.flip_element(-1, axis='vertical', center=(center_x, center_y))
# Type 2 de flip :
# verso_svg_flipped = verso_svg.flip(axis='horizontal')
verso_svg_flipped.generate_svg_file(str(output_path / "verso.svg"))

# 4. Convertir en meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)
verso_path2d = svg_to_path2d(verso_svg_flipped, prepare=False)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)  # 1mm (recto-verso)
verso_mesh = extrude_path(verso_path2d, thickness=1)  # 1mm

# 5. Translater le verso à l'arrière (Z = thickness - verso_thickness)
# Le verso doit être à Z = 3 - 1 = 2mm
translation_matrix = trimesh.transformations.translation_matrix([0, 0, 3 - 1])
verso_mesh.apply_transform(translation_matrix)

# 6. Assembler
plate = assemble_plate(shape_mesh, [recto_mesh, verso_mesh])

# 7. Créer la scène
scene = create_scene([plate, recto_mesh, verso_mesh], view='bottom', tilt=30, rot=0)

# 8. Export
export_stl([plate, recto_mesh, verso_mesh], str(output_path), 
           ['mesh.stl', 'side_A.stl', 'side_B.stl'])

export_html(scene, output_path / "tag_3D_recto_verso.html")

print(f"✓ Tag 3D recto-verso généré dans {output_path}")
print("  - mesh.stl (plaque noire)")
print("  - side_A.stl (texte recto blanc)")
print("  - side_B.stl (texte verso blanc)")
print("  - tag_3D_recto_verso.html (visualisation)")