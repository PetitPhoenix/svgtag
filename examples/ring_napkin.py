"""
Example: Napkin ring with engraved text
Complete workflow from geometry to STL + HTML preview
"""
import numpy as np
from pathlib import Path
import trimesh
from svgtag.geom.shapes import ring_contour
from svgtag.mesh.extrusion import svg_to_path2d, extrude_path
from svgtag.mesh.ring import revolve_ring, wrap_around, create_ring_with_text
from svgtag.mesh.visualization import create_scene, export_html
from svgtag.mesh.colors import DARK_GRAY, OFF_WHITE
from svgtag.svg.base import SVG
from svgtag.svg.text import text_svg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path       = str(ROOT / "static" / "fonts" / "Mocking Bird" / "mocking_bird.ttf")
brand_font_path = str(ROOT / "static" / "fonts" / "Allison" / "Allison-Regular.ttf")

# Parameters
diameter           = 50
height             = 35
thickness          = 6
brand_width        = 30
text               = "Mon prénom"
brand_text         = "Tetsudau"
sections           = 256
text_height_ratio  = 0.6
brand_height_ratio = 0.2
brand_rotation_deg = 60

# Calculate
text_length = np.pi * (diameter - thickness)
R_ext = diameter / 2
R_int = R_ext - thickness
R_med = R_int + 0.25 * thickness

print(f"Ring parameters:")
print(f"  Diameter: {diameter}mm, Height: {height}mm, Thickness: {thickness}mm")
print(f"  Text length (arc): {text_length:.1f}mm")

# 1. Ring geometry
print("\n1. Creating ring geometry...")
vertices, _ = ring_contour(
    height=height, R_ext=R_ext, R_med=R_med, R_int=R_int,
    num_points=20, profile_type='ellipse'
)
ring_mesh = revolve_ring(vertices[:, 0:2], sections=sections)

# 2. Main text SVG
print("\n2. Creating main text SVG...")
text_zone_height = height * text_height_ratio
text_svg_obj = SVG()
text_svg_obj.width   = text_length
text_svg_obj.height  = height
text_svg_obj.viewBox = [0, 0, text_length, height]
text_svg_obj.unit    = "mm"
text_svg_obj.add_svg(text_svg(
    text=text, font_path=font_path, font_size=None,
    zone_width=text_length, zone_height=text_zone_height,
    x0=0, y0=(height - text_zone_height) / 2,
    interline_ratio=0.8, n=1
))
text_svg_obj.update_svg_content()
text_svg_path = output_path / "text.svg"
text_svg_obj.generate_svg_file(str(text_svg_path))

# 3. Brand SVG
print("\n3. Creating brand SVG...")
brand_zone_height = height * brand_height_ratio
brand_svg_obj = SVG()
brand_svg_obj.width   = brand_width
brand_svg_obj.height  = height
brand_svg_obj.viewBox = [0, 0, brand_width, height]
brand_svg_obj.unit    = "mm"
brand_svg_obj.add_svg(text_svg(
    text=brand_text, font_path=brand_font_path, font_size=None,
    zone_width=brand_width, zone_height=brand_zone_height,
    x0=0, y0=(height - brand_zone_height) / 2,
    interline_ratio=0.8, n=None
))
brand_svg_obj.update_svg_content()
brand_svg_path = output_path / "brand.svg"
brand_svg_obj.generate_svg_file(str(brand_svg_path))

# # 4. Main text mesh and wrapping
# print("\n4. Creating and wrapping main text mesh...")
# text_mesh = mesh_from_path(str(text_svg_path), -thickness)
# text_mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [1,0,0]))
# text_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi,    [0,0,1]))
# text_mesh.apply_transform(trimesh.transformations.scale_and_translate(
#     scale=[1,1,1],
#     # translate=[text_length/2, diameter/2 - 0.5*thickness, height/2]
#     translate=[text_length/2, -(diameter/2 - 0.5*thickness), height/2]
# ))
# text_mesh = wrap_around(text_mesh)

# # 5. Brand mesh and wrapping
# print("\n5. Creating and wrapping brand mesh...")
# brand_mesh = mesh_from_path(str(brand_svg_path), -thickness)
# brand_mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [1,0,0]))
# brand_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi,    [0,0,1]))
# brand_mesh.apply_transform(trimesh.transformations.scale_and_translate(
#     scale=[1,1,1],
#     translate=[brand_width/2, -diameter/2 + 0.9*thickness, height*0.2]
# ))
# brand_mesh = wrap_around(brand_mesh)
# brand_mesh.apply_transform(trimesh.transformations.rotation_matrix(
#     brand_rotation_deg * np.pi/180, [0,0,1]
# ))

# 4. Main text mesh
print("\n4. Creating and wrapping main text mesh...")
text_path2d = svg_to_path2d(text_svg_obj)
text_mesh = extrude_path(text_path2d, thickness=-thickness)
text_mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [1,0,0]))
text_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi,    [0,0,1]))
text_mesh.apply_transform(trimesh.transformations.scale_and_translate(
    scale=[1,1,1],
    translate=[text_length/2, diameter/2 - 0.5*thickness, height/2]
))
text_mesh = wrap_around(text_mesh, theta=-np.pi/2)  # face avant -Y

# 5. Brand mesh
print("\n5. Creating and wrapping brand mesh...")
brand_path2d = svg_to_path2d(brand_svg_obj)
brand_mesh = extrude_path(brand_path2d, thickness=-thickness)
brand_mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [1,0,0]))
brand_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi,    [0,0,1]))
brand_mesh.apply_transform(trimesh.transformations.scale_and_translate(
    scale=[1,1,1],
    translate=[brand_width/2, -diameter/2 + 0.9*thickness, height*0.2]
))
brand_mesh = wrap_around(brand_mesh, theta=np.pi/2)  # face arrière +Y
brand_mesh.apply_transform(trimesh.transformations.rotation_matrix(
    brand_rotation_deg * np.pi/180, [0,0,1]
))


# 6. Intersect inserts
print("\n6. Computing inserts...")
text_insert  = trimesh.boolean.intersection([text_mesh,  ring_mesh])
brand_insert = trimesh.boolean.intersection([brand_mesh, ring_mesh])

# 7. Assemble
print("\n7. Assembling ring (boolean subtract)...")
final_ring = create_ring_with_text(ring_mesh, text_mesh, brand_mesh)
# final_ring.show(smooth=False, flags={'wireframe': False, 'axis': True})


# 8. Visualisation
print("\n8. Creating visualization...")
view = 'front'
tilt = 20
rot  = 20

# Interactive debug (uncomment to use):
# scene = create_scene([final_ring], materials=None, view=view, tilt=tilt, rot=rot,
#                         convention='physical')
# scene.show(smooth=False, flags={'wireframe': False, 'axis': True})


scene = create_scene(
    [final_ring, text_insert, brand_insert],
    colors=[DARK_GRAY , OFF_WHITE, OFF_WHITE],
    view=view, tilt=tilt, rot=rot, convention='physical'
)
# scene.show(smooth=False, flags={'wireframe': False, 'axis': True})

export_html(scene, output_path / f"ring_{view}_t{tilt:03d}_r{rot:03d}.html")

from trimesh.viewer import scene_to_html
with open(output_path / 'test_native.html', 'w') as f:
    f.write(scene_to_html(scene))

# 9. Export STL
print("\n9. Exporting STL...")
final_ring.export(str(output_path / "napkin_ring.stl"))
text_insert.export(str(output_path / "text_insert.stl"))
brand_insert.export(str(output_path / "brand_insert.stl"))

print(f"\n✓ Ring generation complete in {output_path}")