"""
Exemples complets de tags : shapes, texte, 3D, brand
Génère tous les types de tags possibles à partir d'une seule configuration
"""
from pathlib import Path
from trimesh import viewer
import trimesh
from svgtag.svg.shapes import tag_circle_svg, tag_rectangle_svg, tag_triangle_svg
from svgtag.svg.composition import add_text_zone, add_outline, add_border_outline
from svgtag.svg.layouts import brand_layout
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate
from svgtag.mesh.visualization import create_scene, export_stl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")
logo_font_path = str(ROOT / "static" / "fonts" / "Allison" / "Allison-Regular.ttf")

# =============================================================================
# CONFIGURATION
# =============================================================================
TAG_TYPE = "circle"  # "circle", "rectangle", "triangle"
LENGTH = 80
HEIGHT = 35
HOLE_DIAMETER = 6
BORDER = 3
CORNER_RADIUS = 3  # Pour rectangle uniquement
TEXT = "Impression d'une étiquette"
BRAND_TEXT = "Tetsudau"
FLIP_AXIS = 'horizontal'  # 'horizontal' pour tag vertical, 'vertical' pour tag horizontal

# =============================================================================
# SETUP
# =============================================================================
output_path = HERE / "outputs" / "tag" / f"tag_{TAG_TYPE}"
output_path.mkdir(parents=True, exist_ok=True)

# Sélection de la fonction de tag
tag_functions = {
    "circle": tag_circle_svg,
    "rectangle": tag_rectangle_svg,
    "triangle": tag_triangle_svg
}

tag_func = tag_functions[TAG_TYPE]

# Arguments communs
common_args = {
    "length": LENGTH,
    "height": HEIGHT,
    "hole_diameter": HOLE_DIAMETER,
    "border": BORDER
}

# Ajouter corner_radius pour rectangle
if TAG_TYPE == "rectangle":
    common_args["corner_radius"] = CORNER_RADIUS

# =============================================================================
# 1. SHAPE ONLY (sans outline)
# =============================================================================
print("Génération 1/6 : Shape only...")
svg, layout = tag_func(**common_args)
svg.generate_svg_file(str(output_path / "01_shape.svg"))

# =============================================================================
# 2. SHAPE + OUTLINE
# =============================================================================
print("Génération 2/6 : Shape + outline...")
svg, layout = tag_func(**common_args)
area = layout.get_area('main')
add_outline(svg, area, color="red")
add_border_outline(svg, area, border=BORDER, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "02_shape_outline.svg"))

# =============================================================================
# 3. SHAPE + TEXT
# =============================================================================
print("Génération 3/6 : Shape + text...")
svg, layout = tag_func(**common_args)
area = layout.get_area('main')
add_text_zone(svg, TEXT, font_path, area)
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "03_with_text.svg"))

# =============================================================================
# 4. SHAPE + TEXT + OUTLINE
# =============================================================================
print("Génération 4/6 : Shape + text + outline...")
svg, layout = tag_func(**common_args)
area = layout.get_area('main')
add_text_zone(svg, TEXT, font_path, area, outline=True)
add_outline(svg, area, color="red")
add_border_outline(svg, area, border=BORDER, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "04_with_text_outline.svg"))

# =============================================================================
# 5. 3D RECTO ONLY
# =============================================================================
print("Génération 5/6 : 3D recto...")
shape_svg, _ = tag_func(**common_args)
_, layout = tag_func(**common_args)

recto_svg = shape_svg.create_empty_copy()
area = layout.get_area('main')
add_text_zone(recto_svg, TEXT, font_path, area)
recto_svg.update_svg_content()

# Meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)

# Assembly
plate = assemble_plate(shape_mesh, [recto_mesh])
scene = create_scene([plate, recto_mesh])

# Export
export_stl([plate, recto_mesh], str(output_path / "05_3d_recto"), 
           ['mesh.stl', 'side_A.stl'])

with open(output_path / "05_3d_recto.html", "w") as f:
    f.write(viewer.scene_to_html(scene))

# =============================================================================
# 6. 3D RECTO-VERSO
# =============================================================================
print("Génération 6/6 : 3D recto-verso...")
shape_svg, _ = tag_func(**common_args)
_, layout = tag_func(**common_args)

recto_svg = shape_svg.create_empty_copy()
area = layout.get_area('main')
add_text_zone(recto_svg, TEXT, font_path, area)
recto_svg.update_svg_content()

# Verso avec flip
verso_svg = shape_svg.create_empty_copy()
add_text_zone(verso_svg, "Recto / Verso", font_path, area, n=1)
verso_svg.update_svg_content()

center_x = area.x + area.width / 2
center_y = area.y + area.height / 2
verso_svg = verso_svg.flip_element(-1, axis='vertical', center=(center_x, center_y))

# Meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)
verso_path2d = svg_to_path2d(verso_svg, prepare=False)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)
verso_mesh = extrude_path(verso_path2d, thickness=1)

# Translation verso
translation_matrix = trimesh.transformations.translation_matrix([0, 0, 3 - 1])
verso_mesh.apply_transform(translation_matrix)

# Assembly
plate = assemble_plate(shape_mesh, [recto_mesh, verso_mesh])
scene = create_scene([plate, recto_mesh, verso_mesh])

# Export
export_stl([plate, recto_mesh, verso_mesh], str(output_path / "06_3d_recto_verso"), 
           ['mesh.stl', 'side_A.stl', 'side_B.stl'])

with open(output_path / "06_3d_recto_verso.html", "w") as f:
    f.write(viewer.scene_to_html(scene))

# =============================================================================
# 7. 3D RECTO + BRAND VERSO
# =============================================================================
print("Génération 7/7 : 3D recto + brand...")
shape_svg, _ = tag_func(**common_args)
_, layout = tag_func(**common_args)

recto_svg = shape_svg.create_empty_copy()
area = layout.get_area('main')
add_text_zone(recto_svg, TEXT, font_path, area)
recto_svg.update_svg_content()

# Brand verso
main_area = layout.get_area('main')
brand_layout_obj = brand_layout(
    main_area=main_area,
    brand_position='bottom-right',
    brand_scale=0.35,
    border=0,
    flip_axis=FLIP_AXIS
)

logo_svg = shape_svg.create_empty_copy()
brand_area = brand_layout_obj.get_area('brand')
add_text_zone(logo_svg, BRAND_TEXT, logo_font_path, brand_area)
logo_svg.update_svg_content()

center_x = brand_area.x + brand_area.width / 2
center_y = brand_area.y + brand_area.height / 2
logo_svg = logo_svg.flip_element(-1, axis=FLIP_AXIS, center=(center_x, center_y))

# Meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)
logo_path2d = svg_to_path2d(logo_svg)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)
logo_mesh = extrude_path(logo_path2d, thickness=1)

# Translation logo
translation_matrix = trimesh.transformations.translation_matrix([0, 0, 3 - 1])
logo_mesh.apply_transform(translation_matrix)

# Assembly
plate = assemble_plate(shape_mesh, [recto_mesh, logo_mesh])
scene = create_scene([plate, recto_mesh, logo_mesh])

# Export
export_stl([plate, recto_mesh, logo_mesh], str(output_path / "07_3d_with_brand"), 
           ['mesh.stl', 'side_A.stl', 'side_B.stl'])

with open(output_path / "07_3d_with_brand.html", "w") as f:
    f.write(viewer.scene_to_html(scene))

# =============================================================================
# RÉSUMÉ
# =============================================================================
print(f"\n✓ Tous les exemples générés dans {output_path}")
print(f"  Type de tag : {TAG_TYPE}")
print(f"  01_shape.svg - Forme seule")
print(f"  02_shape_outline.svg - Forme avec outlines de debug")
print(f"  03_with_text.svg - Forme + texte")
print(f"  04_with_text_outline.svg - Forme + texte + outlines")
print(f"  05_3d_recto/ - Tag 3D recto uniquement")
print(f"  06_3d_recto_verso/ - Tag 3D double face")
print(f"  07_3d_with_brand/ - Tag 3D recto + logo verso")