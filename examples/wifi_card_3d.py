"""
Example: WiFi card 3D generation with brand on back
Generates a 3D printable WiFi card with QR code (front) and brand (back)
"""
from pathlib import Path
import trimesh
from trimesh import viewer
from svgtag.svg.shapes.wifi import wifi_card_svg
from svgtag.svg.text import text_svg
from svgtag.svg.base import SVG
from svgtag.geom.shapes import rounded_rectangle
from svgtag.geom.converters import to_svg
from svgtag.svg.layouts import brand_layout_auto
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.assembly import assemble_plate, create_scene, export_stl
from svgtag.mesh.svg_helpers import prepare_for_trimesh_angles

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

static_files_path = ROOT / "static"
signal_icon_path = static_files_path / "images" / "network.svg"

# Font paths
fonts = {
    'title': static_files_path / "fonts" / "Southmore" / "Southmore.ttf",
    'subtitle': static_files_path / "fonts" / "BillionDreams" / "BillionDreams.ttf",
    'label': static_files_path / "fonts" / "Stark" / "Stark.ttf",
    'value': static_files_path / "fonts" / "Kollektif" / "Kollektif.ttf",
    'brand': static_files_path / "fonts" / "Allison" / "Allison-Regular.ttf",
}

# Text configuration
texts = {
    'title': {'text': 'Bienvenue', 'font_size': 30},
    'subtitle': {'text': 'Profitez du wifi', 'font_size': 20},
    'network_label': {'text': 'Réseau', 'font_size': 20},
    'password_label': {'text': 'Mot de passe', 'font_size': 20},
}

# WiFi parameters
network = "MyNetwork"
password = "MyPassword"
protocol = "WPA"
hidden = False

# 3D parameters
width_mm = 100
height_mm = 100
thickness = 3

padding_mm = 5
corner_radius = 3

print(f"Generating 3D WiFi card...")
print(f"  Network: {network}")
print(f"  Password: {password}")
print(f"  Dimensions: {width_mm}x{height_mm}x{thickness}mm")

# 1. Create base shape (rounded rectangle)
print("\n1. Creating base shape...")
shape_geom = rounded_rectangle(
    width=width_mm,
    height=height_mm,
    corner_radius=corner_radius,
    x=0,
    y=0
)
shape_svg = to_svg(shape_geom, width_mm, height_mm)
shape_path2d = svg_to_path2d(shape_svg)
shape_mesh = extrude_path(shape_path2d, thickness)
print(f"   Shape mesh: {len(shape_mesh.vertices)} vertices")

# 2. Generate FRONT face (QR code + text)
print("\n2. Creating front face (QR code + text)...")
face_svg, layout = wifi_card_svg(
    network=network,
    password=password,
    width_mm=width_mm,
    height_mm=height_mm,
    padding_mm=padding_mm,
    protocol=protocol,
    hidden=hidden,
    signal_icon_path=str(signal_icon_path)
)

# Add all text elements to front
title_area = layout.get_area('title')
title_svg = text_svg(
    text=texts['title']['text'],
    font_path=str(fonts['title']),
    font_size=texts['title']['font_size'],
    zone_width=title_area.width,
    zone_height=title_area.height,
    x0=title_area.x,
    y0=title_area.y
)
face_svg.add_group(title_svg.elements)

subtitle_area = layout.get_area('subtitle')
subtitle_svg = text_svg(
    text=texts['subtitle']['text'],
    font_path=str(fonts['subtitle']),
    font_size=texts['subtitle']['font_size'],
    zone_width=subtitle_area.width,
    zone_height=subtitle_area.height,
    x0=subtitle_area.x,
    y0=subtitle_area.y
)
face_svg.add_group(subtitle_svg.elements)

network_label_area = layout.get_area('network_label')
network_label_svg = text_svg(
    text=texts['network_label']['text'],
    font_path=str(fonts['label']),
    font_size=texts['network_label']['font_size'],
    zone_width=network_label_area.width,
    zone_height=network_label_area.height,
    x0=network_label_area.x,
    y0=network_label_area.y
)
face_svg.add_group(network_label_svg.elements)

network_value_area = layout.get_area('network_value')
network_value_svg = text_svg(
    text=network,
    font_path=str(fonts['value']),
    font_size=14,
    zone_width=network_value_area.width,
    zone_height=network_value_area.height,
    x0=network_value_area.x,
    y0=network_value_area.y
)
face_svg.add_group(network_value_svg.elements)

password_label_area = layout.get_area('password_label')
password_label_svg = text_svg(
    text=texts['password_label']['text'],
    font_path=str(fonts['label']),
    font_size=texts['password_label']['font_size'],
    zone_width=password_label_area.width,
    zone_height=password_label_area.height,
    x0=password_label_area.x,
    y0=password_label_area.y
)
face_svg.add_group(password_label_svg.elements)

password_value_area = layout.get_area('password_value')
password_value_svg = text_svg(
    text=password,
    font_path=str(fonts['value']),
    font_size=14,
    zone_width=password_value_area.width,
    zone_height=password_value_area.height,
    x0=password_value_area.x,
    y0=password_value_area.y
)
face_svg.add_group(password_value_svg.elements)

# Save front face SVG
face_svg.generate_svg_file(str(output_path / "face_front.svg"))

# Prepare front for trimesh
face_svg_prepared = prepare_for_trimesh_angles(face_svg)
face_path2d = svg_to_path2d(face_svg_prepared)
face_mesh = extrude_path(face_path2d, 1)  # Depth 1mm
print(f"   Front face mesh: {len(face_mesh.vertices)} vertices")

# 3. Generate BACK face (brand)
print("\n3. Creating back face (brand)...")
# Create empty SVG for back
back_svg = SVG()
back_svg.width = width_mm
back_svg.height = height_mm
back_svg.viewBox = [0, 0, width_mm, height_mm]
back_svg.unit = "mm"

# Main area for brand positioning (full card)
from svgtag.svg.layout import PrintableArea
main_area = PrintableArea(
    x=padding_mm,
    y=padding_mm,
    width=width_mm - 2 * padding_mm,
    height=height_mm - 2 * padding_mm
)

# Create brand layout (auto-sized, bottom-right)
brand_layout_obj, brand_width, brand_height = brand_layout_auto(
    main_area=main_area,
    text="Tetsudau",
    font_path=str(fonts['brand']),
    brand_position='bottom-right',
    brand_width_scale=0.35,
    border=2,
    flip_axis='vertical',  # Important for back face
    n=None
)

brand_area = brand_layout_obj.get_area('brand')

# Add brand text
brand_text_svg = text_svg(
    text="Tetsudau",
    font_path=str(fonts['brand']),
    font_size=None,  # Auto-fit
    zone_width=brand_width,
    zone_height=brand_height,
    x0=brand_area.x,
    y0=brand_area.y
)
back_svg.add_group(brand_text_svg.elements)

# Save back face SVG
back_svg.generate_svg_file(str(output_path / "face_back.svg"))

# Prepare back for trimesh (flip for extrusion)
back_svg_prepared = prepare_for_trimesh_angles(back_svg)
back_svg_flipped = back_svg_prepared.flip(axis='vertical')  # Flip for back face

back_path2d = svg_to_path2d(back_svg_flipped)
back_mesh = extrude_path(back_path2d, 1)  # Depth 1mm

# Translater le brand au dos (à Z = thickness)
back_mesh.apply_transform(
    trimesh.transformations.translation_matrix([0, 0, thickness - 1])
)

print(f"   Back face mesh: {len(back_mesh.vertices)} vertices (translated to Z={thickness})")

# 4. Assemble
print("\n4. Assembling plate...")
try:
    final_plate = assemble_plate(shape_mesh, [face_mesh, back_mesh])
    print(f"   Final mesh: {len(final_plate.vertices)} vertices")
    
    if len(final_plate.vertices) == len(shape_mesh.vertices):
        print("   ⚠️  Warning: Boolean subtract may have failed (same vertex count)")
    else:
        print(f"   ✓ Assembly successful ({len(shape_mesh.vertices)} → {len(final_plate.vertices)} vertices)")
        
except Exception as e:
    print(f"   ✗ Assembly failed: {e}")
    print("   Using shape mesh as fallback")
    final_plate = shape_mesh

# 5. Create scene with colors
print("\n5. Creating visualization scene...")
colors = [
    [48, 48, 48],      # Plate: dark gray
    [248, 248, 241],   # Front face: off-white
    [248, 248, 241],   # Back face: off-white
]
scene = create_scene([final_plate, face_mesh, back_mesh], colors=colors)

# 6. Export
print("\n6. Exporting files...")

# STL files
export_stl(
    [final_plate, face_mesh, back_mesh], 
    str(output_path), 
    names=['wifi_card.stl', 'face_front.stl', 'face_back.stl']
)

# HTML visualization
html_path = output_path / "wifi_card_3d.html"
with open(html_path, "w") as f:
    f.write(viewer.scene_to_html(scene))

print(f"\n✓ Files generated in {output_path}:")
print(f"  - wifi_card.stl (final plate)")
print(f"  - face_front.stl (front text layer)")
print(f"  - face_back.stl (back brand layer)")
print(f"  - wifi_card_3d.html (3D preview)")
print(f"  - face_front.svg (reference)")
print(f"  - face_back.svg (reference)")