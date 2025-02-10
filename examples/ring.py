import os
from SVGtag.generators.ring import ring, export
    
# Define inputs
diameter = 50
height = 35
thickness = 6
res = 20  # max: 26
# FONT = '../static/fonts/Impact/impact.ttf'
font_dir = '../static/fonts'
font = 'Mocking Bird/mocking_bird.ttf'
text = "Mon prénom"

# Define outputs
output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'ring')
os.makedirs(output_path, exist_ok=True)
id = 1
filename = f"{text.lower()}-{id:02d}"

# Process
mesh = ring(text, diameter, height, thickness, res, font_dir, font, output_path, filename, shape=1, brand=True, vis=False)
export(mesh, style='html', path = output_path, name = filename)