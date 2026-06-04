"""
Example: generic QR card 3D generation with brand on back.

Same recipe as `wifi_card_3d.py`, but built on the payload-agnostic
`qr_card_svg(payload, ...)`: here the QR encodes an arbitrary URL. Swap `payload`
for any other string (mailto:, tel:, SMSTO:, BEGIN:VCARD..., geo:, raw text, or
the WiFi `WIFI:...` format) to make a different card — the rest is identical.
"""
from pathlib import Path
import trimesh
from trimesh import viewer
from svgtag.svg.shapes.qr import qr_card_svg
from svgtag.svg.text import text_svg
from svgtag.svg.base import SVG
from svgtag.svg.layout import PrintableArea
from svgtag.svg.layouts import brand_layout_auto
from svgtag.geom.shapes import rounded_rectangle
from svgtag.geom.converters import to_svg
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate
from svgtag.mesh.visualization import create_scene, export_stl
from svgtag.mesh.svg_helpers import prepare_for_trimesh_angles

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

static_files_path = ROOT / "static"

# Font paths
fonts = {
    'title': static_files_path / "fonts" / "Southmore" / "Southmore.ttf",
    'label': static_files_path / "fonts" / "Stark" / "Stark.ttf",
    'value': static_files_path / "fonts" / "Kollektif" / "Kollektif.ttf",
    'brand': static_files_path / "fonts" / "Allison" / "Allison-Regular.ttf",
}

# --- Payload : n'importe quelle chaîne. Ici une URL. -----------------------
# Autres exemples :
#   payload = "mailto:contact@tetsudau.fr?subject=Bonjour"
#   payload = "tel:+33600000000"
#   payload = "BEGIN:VCARD\nVERSION:3.0\nFN:Stéphane\nTEL:+33600000000\nEND:VCARD"
#   payload = "geo:48.8566,2.3522"
url = "https://github.com/PetitPhoenix/svgtag"
payload = url

# Text configuration (gravé sur le recto, à gauche du QR)
texts = {
    'title': {'text': 'Scannez-moi', 'font_size': 36},
    'label': {'text': 'Lien',        'font_size': 20},
    # URL complète (schéma compris) — le QR encode la même chaîne
    'value': {'text': url, 'font_size': 14},
}

# 3D parameters
width_mm = 120
height_mm = 120
thickness = 3
padding_mm = 5
corner_radius = 3

print("Generating 3D QR card...")
print(f"  Payload: {payload}")
print(f"  Dimensions: {width_mm}x{height_mm}x{thickness}mm")

# 1. Base shape (rounded rectangle)
print("\n1. Creating base shape...")
shape_geom = rounded_rectangle(width=width_mm, height=height_mm,
                               corner_radius=corner_radius, x=0, y=0)
shape_mesh = extrude_path(svg_to_path2d(to_svg(shape_geom, width_mm, height_mm)), thickness)
print(f"   Shape mesh: {len(shape_mesh.vertices)} vertices")

# 2. FRONT face (QR code + text)
print("\n2. Creating front face (QR code + text)...")
face_svg, layout = qr_card_svg(
    payload,
    width_mm=width_mm,
    height_mm=height_mm,
    padding_mm=padding_mm,
    icon_path=None,   # mets une icône SVG ici pour la graver en haut à droite
)

for zone, font_key in (('title', 'title'), ('network_label', 'label'), ('network_value', 'value')):
    area = layout.get_area(zone)
    if area is None:
        continue
    cfg = texts['title' if zone == 'title' else ('label' if zone.endswith('label') else 'value')]
    t = text_svg(
        text=cfg['text'], font_path=str(fonts[font_key]), font_size=cfg['font_size'],
        zone_width=area.width, zone_height=area.height, x0=area.x, y0=area.y,
    )
    face_svg.add_group(t.elements)

face_svg.generate_svg_file(str(output_path / "face_front.svg"))

face_svg_prepared = prepare_for_trimesh_angles(face_svg)
face_mesh = extrude_path(svg_to_path2d(face_svg_prepared), 1)  # 1mm deep
print(f"   Front face mesh: {len(face_mesh.vertices)} vertices")

# 3. BACK face (brand)
print("\n3. Creating back face (brand)...")
back_svg = SVG()
back_svg.width = width_mm
back_svg.height = height_mm
back_svg.viewBox = [0, 0, width_mm, height_mm]
back_svg.unit = "mm"

main_area = PrintableArea(x=padding_mm, y=padding_mm,
                          width=width_mm - 2 * padding_mm,
                          height=height_mm - 2 * padding_mm)
brand_layout_obj, brand_width, brand_height = brand_layout_auto(
    main_area=main_area, text="Tetsudau", font_path=str(fonts['brand']),
    brand_position='bottom-right', brand_width_scale=0.35, border=2,
    flip_axis='vertical', n=None,
)
brand_area = brand_layout_obj.get_area('brand')
brand_text_svg = text_svg(
    text="Tetsudau", font_path=str(fonts['brand']), font_size=None,
    zone_width=brand_width, zone_height=brand_height, x0=brand_area.x, y0=brand_area.y,
)
back_svg.add_group(brand_text_svg.elements)
back_svg.generate_svg_file(str(output_path / "face_back.svg"))

back_svg_prepared = prepare_for_trimesh_angles(back_svg)
back_svg_flipped = back_svg_prepared.flip(axis='vertical')
back_mesh = extrude_path(svg_to_path2d(back_svg_flipped), 1)
back_mesh.apply_transform(trimesh.transformations.translation_matrix([0, 0, thickness - 1]))
print(f"   Back face mesh: {len(back_mesh.vertices)} vertices (translated to Z={thickness})")

# 4. Assemble
print("\n4. Assembling plate...")
try:
    final_plate = assemble_plate(shape_mesh, [face_mesh, back_mesh])
    if len(final_plate.vertices) == len(shape_mesh.vertices):
        print("   ⚠️  Warning: Boolean subtract may have failed (same vertex count)")
    else:
        print(f"   ✓ Assembly successful ({len(shape_mesh.vertices)} → {len(final_plate.vertices)} vertices)")
except Exception as e:
    print(f"   ✗ Assembly failed: {e}")
    final_plate = shape_mesh

# 5. Scene
print("\n5. Creating visualization scene...")
colors = [
    [48, 48, 48],     # Plate: dark gray
    [248, 248, 241],  # Front face: off-white
    [248, 248, 241],  # Back face: off-white
]
scene = create_scene([final_plate, face_mesh, back_mesh], colors=colors)

# 6. Export
print("\n6. Exporting files...")
export_stl([final_plate, face_mesh, back_mesh], str(output_path),
           names=['qr_card.stl', 'face_front.stl', 'face_back.stl'])
with open(output_path / "qr_card_3d.html", "w") as f:
    f.write(viewer.scene_to_html(scene))

print(f"\n✓ Files generated in {output_path}:")
print("  - qr_card.stl (final plate)")
print("  - face_front.stl (front text layer)")
print("  - face_back.stl (back brand layer)")
print("  - qr_card_3d.html (3D preview)")
print("  - face_front.svg / face_back.svg (reference)")
