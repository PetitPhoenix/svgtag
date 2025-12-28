"""
Example: Napkin ring with engraved text
Complete workflow from geometry to STL + HTML preview
"""
import numpy as np
from pathlib import Path
import trimesh
from trimesh import viewer
from svgtag.geom.shapes import ring_contour
from svgtag.mesh.ring import revolve_ring, wrap_around, mesh_from_path, create_ring_with_text
from svgtag.svg.base import SVG
from svgtag.svg.text import text_svg
# TODO: a bit of cleanup and put generators in other folders

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Mocking Bird" / "mocking_bird.ttf")
brand_font_path = str(ROOT / "static" / "fonts" / "Allison" / "Allison-Regular.ttf")

# Parameters
diameter = 50    # mm
height = 35      # mm
thickness = 6    # mm
brand_width = 30 # mm
text = "Tetsudau"
brand_text = "Tetsudau"
sections = 256
text_height_ratio = 0.6
brand_height_ratio = 0.2
brand_rotation_deg = 60

# Calculate
text_length = np.pi * (diameter - thickness)
R_ext = diameter / 2
R_int = R_ext - thickness
R_med = R_int + 0.25 * thickness

print(f"Ring parameters:")
print(f"  Diameter: {diameter}mm")
print(f"  Height: {height}mm")
print(f"  Thickness: {thickness}mm")
print(f"  Text length (arc): {text_length:.1f}mm")
print(f"  Text height: {height * text_height_ratio:.1f}mm")

# 1. Ring geometry
print("\n1. Creating ring geometry...")
vertices, _ = ring_contour(
    height=height,
    R_ext=R_ext,
    R_med=R_med,
    R_int=R_int,
    num_points=20,
    profile_type='ellipse'
)
ring_mesh = revolve_ring(vertices[:, 0:2], sections=sections)
print(f"   Ring mesh: {len(ring_mesh.vertices)} vertices")

# 2. Main text SVG
print("\n2. Creating main text SVG...")
text_zone_height = height * text_height_ratio
text_y_offset = (height - text_zone_height) / 2

text_svg_obj = SVG()
text_svg_obj.width = text_length
text_svg_obj.height = height
text_svg_obj.viewBox = [0, 0, text_length, height]
text_svg_obj.unit = "mm"

text_content = text_svg(
    text=text,
    font_path=font_path,
    font_size=None,
    zone_width=text_length,
    zone_height=text_zone_height,
    x0=0,
    y0=text_y_offset,
    interline_ratio=0.8,
    n=None
)

text_svg_obj.add_svg(text_content)
text_svg_obj.update_svg_content()

text_svg_path = output_path / "text.svg"
text_svg_obj.generate_svg_file(str(text_svg_path))
print(f"   Main text SVG saved: {text_svg_path}")

# 3. Brand SVG (petit, 20% hauteur)
print("\n3. Creating brand SVG...")
brand_zone_height = height * brand_height_ratio
brand_y_offset = (height - brand_zone_height) / 2

brand_svg_obj = SVG()
brand_svg_obj.width = brand_width
brand_svg_obj.height = height
brand_svg_obj.viewBox = [0, 0, brand_width, height]
brand_svg_obj.unit = "mm"

brand_content = text_svg(
    text=brand_text,
    font_path=brand_font_path,
    font_size=None,
    zone_width=brand_width,
    zone_height=brand_zone_height,
    x0=0,
    y0=brand_y_offset,
    interline_ratio=0.8,
    n=None
)

brand_svg_obj.add_svg(brand_content)
brand_svg_obj.update_svg_content()

brand_svg_path = output_path / "brand.svg"
brand_svg_obj.generate_svg_file(str(brand_svg_path))
print(f"   Brand SVG saved: {brand_svg_path}")

# 4. Main text mesh and wrapping
print("\n4. Creating and wrapping main text mesh...")
text_mesh = mesh_from_path(str(text_svg_path), -thickness)

text_mesh = text_mesh.apply_transform(
    trimesh.transformations.rotation_matrix(angle=-np.pi / 2, direction=[1, 0, 0])
)
text_mesh = text_mesh.apply_transform(
    trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1])
)
text_mesh = text_mesh.apply_transform(
    trimesh.transformations.scale_and_translate(
        scale=[1, 1, 1],
        translate=[text_length / 2, diameter / 2 - 0.5 * thickness, height / 2]
    )
)
text_mesh = wrap_around(text_mesh)
print(f"   Main text mesh wrapped: {len(text_mesh.vertices)} vertices")

# 5. Brand mesh and wrapping (opposé, en bas, tourné de 120°)
print("\n5. Creating and wrapping brand mesh...")
brand_mesh = mesh_from_path(str(brand_svg_path), -thickness)

brand_mesh = brand_mesh.apply_transform(
    trimesh.transformations.rotation_matrix(angle=-np.pi / 2, direction=[1, 0, 0])
)
brand_mesh = brand_mesh.apply_transform(
    trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1])
)
# Position brand en bas
brand_z_offset = height * 0.2
brand_mesh = brand_mesh.apply_transform(
    trimesh.transformations.scale_and_translate(
        scale=[1, 1, 1],
        translate=[brand_width / 2, -diameter / 2 + 0.9 * thickness, brand_z_offset]
    )
)
brand_mesh = wrap_around(brand_mesh)

brand_mesh = brand_mesh.apply_transform(
    trimesh.transformations.rotation_matrix(
        angle=brand_rotation_deg * np.pi / 180,
        direction=[0, 0, 1]
    )
)
print(f"   Brand mesh wrapped and rotated: {len(brand_mesh.vertices)} vertices")

# 6. Assemble
print("\n6. Assembling ring (boolean subtract)...")
final_ring = create_ring_with_text(ring_mesh, text_mesh, brand_mesh)
print(f"   Final mesh: {len(final_ring.vertices)} vertices")

# 7. Create scene for visualization
print("\n7. Creating visualization...")
ring_mesh.visual.face_colors = [240, 240, 240, 255]
text_mesh.visual.face_colors = [255, 38, 75, 255]
brand_mesh.visual.face_colors = [75, 150, 255, 255]  # Bleu pour brand
final_ring.visual.face_colors = [48, 48, 48, 255]

scene = trimesh.Scene()
scene.add_geometry([final_ring, text_mesh, brand_mesh])

# Position camera
R = trimesh.transformations.concatenate_matrices(
    trimesh.transformations.rotation_matrix(angle=-np.pi / 3, direction=[1, 0, 0]),
    trimesh.transformations.rotation_matrix(angle=np.pi / 4, direction=[0, 0, 1])
)
R[0:3, 3] = [0, 1.5 * diameter, 1.5 * height]
scene.camera_transform = R

# 8. Export
print("\n8. Exporting files...")

# STL
stl_path = output_path / "napkin_ring.stl"
final_ring.export(str(stl_path))
print(f"   ✓ STL: {stl_path}")

# HTML preview
html_path = output_path / "napkin_ring.html"
with open(html_path, "w") as f:
    f.write(viewer.scene_to_html(scene))
print(f"   ✓ HTML: {html_path}")

print(f"\n✓ Ring generation complete!")