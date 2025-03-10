import os
from svgtag.generators.ring import ring, export
    
# Define inputs
diameter = 50
height = 35
thickness = 6
res = 20  # max: 26
# FONT = '../static/fonts/Impact/impact.ttf'
font_dir = '../static/fonts'
font = 'Mocking Bird/mocking_bird.ttf'
text = "Test"

# Define outputs
output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'ring')
os.makedirs(output_path, exist_ok=True)
id = 1
filename = f"{text.lower()}-{id:02d}"

# Process
mesh = ring(text, diameter, height, thickness, res, font_dir, font, output_path, filename, shape=2, brand=True, vis=False)

import trimesh
material = trimesh.visual.material.SimpleMaterial(diffuse=[0.8, 0.8, 0.8], ambient=[1, 1, 1], specular=None, glossiness=1)# PBRMaterial(name="PLA")
mesh.visual.material = material
# mesh.visual.face_colors = [48, 48, 48, 255]
mesh.visual.face_colors = [248, 248, 241, 255]

# scene, data = export(mesh, style='scene', path=None, name=None)

export(mesh, style='html', path = output_path, name = filename)









