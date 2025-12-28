"""
Exemple: Tablette narcose 3D avec brand
Génère une tablette de test de narcose avec titre, consignes, numéros et logo verso
"""
from pathlib import Path
from trimesh import viewer
import trimesh
from svgtag.svg.shapes import tablet_svg
from svgtag.svg.composition import add_text_zone
from svgtag.svg.text import text_svg
from svgtag.svg.layouts import brand_layout_auto
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate, create_scene, export_stl
from svgtag.utils.numbers import generate_test_set

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tablet" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")
logo_font_path = str(ROOT / "static" / "fonts" / "Allison" / "Allison-Regular.ttf")
chaines = generate_test_set('moyen', n=10, seed=42)

# =============================================================================
# 1. SHAPE (forme vide)
# =============================================================================
shape_svg, _ = tablet_svg(
    width=80,
    height=129,
    padding=3,
    eyelet_outer_diameter=18,
    eyelet_hole_diameter=8,
    ear_offset=[5, 5],
    layout_type='narcose'
)

# =============================================================================
# 2. RECTO (titre + consignes + numéros)
# =============================================================================
_, layout = tablet_svg(
    width=80,
    height=129,
    padding=3,
    eyelet_outer_diameter=18,
    eyelet_hole_diameter=8,
    ear_offset=[5, 5],
    layout_type='narcose'
)

recto_svg = shape_svg.create_empty_copy()

# Titre
title_area = layout.get_area('title')
add_text_zone(recto_svg, "Test de Narcose", font_path, title_area, n=1, text_scale=0.4)

# Consignes (texte latéral gauche)
side_area = layout.get_area('side_text')
add_text_zone(recto_svg, "Recopier le maximum de chiffres en 2 minutes !\nA faire au fond et en surface, 1 pt si pas d'erreur.", font_path, side_area, n=2, text_scale=0.8)

# Numéros
main_text_area = layout.get_area('main_text')
svg_numbers = text_svg(
    text=" ".join(chaines),
    font_path=font_path,
    font_size=None,
    zone_width=main_text_area.width,
    zone_height=main_text_area.height,
    x0=main_text_area.x,
    y0=main_text_area.y,
    interline_ratio=1.0,
    n=len(chaines)
)
recto_svg.add_svg(svg_numbers)

recto_svg.update_svg_content()

# =============================================================================
# 3. VERSO (brand/logo)
# =============================================================================
flip_axis = 'vertical'  # Pour tablette horizontale

# Utiliser la zone 'main' pour le brand (toute la surface)
main_area = layout.get_area('main')

brand_layout_obj, tw, th = brand_layout_auto(
    main_area=main_area,
    text="Tetsudau",
    font_path=logo_font_path,
    brand_position='bottom-right',
    brand_width_scale=0.35,
    border=0,
    flip_axis=flip_axis,
)

logo_svg = shape_svg.create_empty_copy()
brand_area = brand_layout_obj.get_area('brand')
add_text_zone(logo_svg, "Tetsudau", logo_font_path, brand_area)
logo_svg.update_svg_content()

# Flip l'élément texte autour du centre de la brand area
center_x = brand_area.x + brand_area.width / 2
center_y = brand_area.y + brand_area.height / 2
logo_svg = logo_svg.flip_element(-1, axis=flip_axis, center=(center_x, center_y))

# =============================================================================
# 4. SAUVEGARDER SVG (debug)
# =============================================================================
shape_svg.generate_svg_file(str(output_path / "shape.svg"))
recto_svg.generate_svg_file(str(output_path / "recto.svg"))
logo_svg.generate_svg_file(str(output_path / "verso.svg"))

print(f"✓ SVG sauvegardés:")
print(f"  - shape.svg (viewBox: {shape_svg.viewBox})")
print(f"  - recto.svg (viewBox: {recto_svg.viewBox})")
print(f"  - verso.svg (viewBox: {logo_svg.viewBox})")

# =============================================================================
# 5. GÉNÉRATION 3D
# =============================================================================
# Convertir en meshes
shape_path2d = svg_to_path2d(shape_svg)
recto_path2d = svg_to_path2d(recto_svg)
logo_path2d = svg_to_path2d(logo_svg)

shape_mesh = extrude_path(shape_path2d, thickness=3)
recto_mesh = extrude_path(recto_path2d, thickness=1)
logo_mesh = extrude_path(logo_path2d, thickness=1)

# Translater le logo à l'arrière
translation_matrix = trimesh.transformations.translation_matrix([0, 0, 3 - 1])
logo_mesh.apply_transform(translation_matrix)

# Assembler
plate = assemble_plate(shape_mesh, [recto_mesh, logo_mesh])

# Créer la scène
scene = create_scene([plate, recto_mesh, logo_mesh])

# Export STL
export_stl([plate, recto_mesh, logo_mesh], str(output_path), 
           ['mesh.stl', 'side_A.stl', 'side_B.stl'])

# Sauvegarder visualisation HTML
with open(output_path / "narcose_3d.html", "w") as f:
    f.write(viewer.scene_to_html(scene))

print(f"\n✓ Fichiers 3D générés dans: {output_path}")
print("  - mesh.stl (plaque noire)")
print("  - side_A.stl (titre + consignes + numéros blancs)")
print("  - side_B.stl (logo blanc)")
print("  - narcose_3d.html (visualisation)")