import os
from trimesh import viewer # if not written, error in import
from svgtag.generators.tag import svg2stl, tag

# General setup
output_path = './outputs/tag'
font_path = '../static/fonts/Impact/impact.ttf'
logo_font_path = '../static/fonts/Allison/Allison-Regular.ttf'

# Define the dimensions and properties for the tag
text = "Impression d'une étiquette"
width_mm = 80
height_mm = 35
thk = 3
shape = 'circle'
phi = 5

# Generate simple svg tag
shape = tag("", font_path, width_mm, height_mm, phi, shape="circle", outline=False)
shape.generate_svg_file(os.path.join(output_path, "shape.svg"))

svgtag = tag(text, font_path, width_mm, height_mm, phi, shape="circle", outline=True)
svgtag.generate_svg_file(os.path.join(output_path, "tag_txt.svg"))


txttag = tag(text, font_path, width_mm, height_mm, 0, shape=None, outline=False)
txttag.generate_svg_file(os.path.join(output_path, "tag_txt_R.svg"))

textlogo = "Tetsudau"
txttag = tag(textlogo, logo_font_path, width_mm, height_mm, 0, shape=None, outline=False)
txttag.generate_svg_file(os.path.join(output_path, "logo.svg"))

scene = svg2stl(
    os.path.join(output_path, "shape.svg"),
    thickness=3,
    output_path=output_path,
    side_A=os.path.join(output_path, "tag_txt_R.svg"),
    side_B=os.path.join(output_path, "logo.svg"),
    brand=True,
)

with open(
    os.path.join(output_path, "tag_3D_recto_verso_brand.html"), "w"
) as file:
    file.write(viewer.scene_to_html(scene))
