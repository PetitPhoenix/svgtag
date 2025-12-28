"""
Exemple: Tag 3D avec logo/brand
Crée un tag 3D avec texte recto et petit logo verso
"""
from pathlib import Path
from trimesh import viewer
import trimesh
from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone, add_outline
from svgtag.svg.layouts import brand_layout
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate, create_scene, export_stl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")
logo_font_path = str(ROOT / "static" / "fonts" / "Allison" / "Allison-Regular.ttf")

# 1. Créer la forme
shape_svg, _ = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)

# 2. Créer le recto
_, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)

recto_svg = shape_svg.create_empty_copy()
area = layout.get_area('main')
add_text_zone(recto_svg, "Impression d'une étiquette", font_path, area)
recto_svg.update_svg_content()

# 3. Créer le logo (verso) avec brand_layout
# Position finale souhaitée : bottom-right VU DE DERRIÈRE
flip_axis = 'horizontal'  # ou 'vertical'
main_area = layout.get_area('main')

brand_layout_obj = brand_layout(
    main_area=main_area,
    brand_position='bottom-right',
    brand_scale=0.35,
    border=0,
    flip_axis=flip_axis
)

logo_svg = shape_svg.create_empty_copy()
brand_area = brand_layout_obj.get_area('brand')
add_text_zone(logo_svg, "Tetsudau", logo_font_path, brand_area)
logo_svg.update_svg_content()

# Flip juste l'élément texte autour du centre de la brand area
center_x = brand_area.x + brand_area.width / 2
center_y = brand_area.y + brand_area.height / 2
logo_svg = logo_svg.flip_element(-1, axis=flip_axis, center=(center_x, center_y))

# 4. Convertir en meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)
logo_path2d = svg_to_path2d(logo_svg)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)
logo_mesh = extrude_path(logo_path2d, thickness=1)

# 5. Translater le logo à l'arrière (Z = thickness - logo_thickness)
translation_matrix = trimesh.transformations.translation_matrix([0, 0, 3 - 1])
logo_mesh.apply_transform(translation_matrix)

# 6. Assembler
plate = assemble_plate(shape_mesh, [recto_mesh, logo_mesh])

# 7. Créer la scène
scene = create_scene([plate, recto_mesh, logo_mesh])

# 8. Export
export_stl([plate, recto_mesh, logo_mesh], str(output_path), 
           ['mesh.stl', 'side_A.stl', 'side_B.stl'])

with open(output_path / "tag_3D_with_brand.html", "w") as file:
    file.write(viewer.scene_to_html(scene))

print(f"✓ Tag 3D avec brand généré dans {output_path}")
print("  - mesh.stl (plaque noire)")
print("  - side_A.stl (texte recto blanc)")
print("  - side_B.stl (logo blanc petit en bottom-right)")
print("  - tag_3D_with_brand.html (visualisation)")