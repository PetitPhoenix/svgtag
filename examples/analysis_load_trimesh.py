
# log_file_path = 'analysis_log_trimesh.log'
# sys.stdout = open(log_file_path, 'w')
# Contenu du fichier SVG avec un rectangle
# svg_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
# <svg
#    width="81"
#    height="81"
#    version="1.1"
#    id="svg192"
#    sodipodi:docname="test.svg"
#    xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
#    xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
#    xmlns="http://www.w3.org/2000/svg"
#    xmlns:svg="http://www.w3.org/2000/svg">
#   <defs
#      id="defs196" />
#   <rect
#      x="0.5"
#      y="0.5"
#      width="80"
#      height="80"
#      fill="none"
#      stroke="#000000"
#      stroke-width="1"
#      id="rect190" />
# </svg>
# """

# script_path = os.path.abspath(__file__)
# script_dir = os.path.dirname(script_path)
# os.chdir(script_dir)




# ça marche

import os
import trimesh
from trimesh import viewer # if not written, error in import
import sys

os.chdir(r'C:\TOOLS\Perso\SVGtag\examples')
svg_path = r'./outputs/shape_ink.svg'
path = trimesh.load_path(svg_path, file_type='svg')
print("Path loaded")
# os.remove(svg_path)
# print("Deleted svg")
mesh = path.extrude(3)
print("Mesh extruded")
mesh.export('./outputs/test.stl')
print("STL exported")
scene = trimesh.Scene(mesh)
with open('./outputs/test.html', "w") as file:
    file.write(trimesh.viewer.scene_to_html(scene))
print("HTML exported")



# test open file => ça marche

import os
import trimesh
from trimesh import viewer # if not written, error in import
import sys

os.chdir(r'C:\TOOLS\Perso\SVGtag\examples')
svg_path = r'./outputs/shape_ink.svg'
with open(svg_path, "rb") as file:
    path = trimesh.path.exchange.load.load_path(file, file_type='svg')
print("Path loaded")
os.remove(svg_path)
print("Deleted svg")
mesh = path.extrude(3)
print("Mesh extruded")
mesh.export('./outputs/test.stl')
print("STL exported")
scene = trimesh.Scene(mesh)
with open('./outputs/test.html', "w") as file:
    file.write(trimesh.viewer.scene_to_html(scene))
print("HTML exported")



# test open file => ça marche

import os
import trimesh
from trimesh import viewer # if not written, error in import
import sys

os.chdir(r'C:\TOOLS\Perso\SVGtag\examples')
svg_path = r'./outputs/shape_ink.svg'
with open(svg_path, "rb") as file:
    path = trimesh.load_path(file, file_type='svg')
print("Path loaded")
os.remove(svg_path)
print("Deleted svg")
mesh = path.extrude(3)
print("Mesh extruded")
mesh.export('./outputs/test.stl')
print("STL exported")
scene = trimesh.Scene(mesh)
with open('./outputs/test.html', "w") as file:
    file.write(trimesh.viewer.scene_to_html(scene))
print("HTML exported")

# carré simple => NOK
import os
import trimesh
from trimesh import viewer # if not written, error in import
import sys

svg_content = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="1"/>
</svg>"""
os.chdir(r'C:\TOOLS\Perso\SVGtag\examples')
svg_path = r'./outputs/test.svg'
path = trimesh.load_path(svg_path, file_type='svg')
print("Path loaded")
# os.remove(svg_path)
# print("Deleted svg")
mesh = path.extrude(3)
print("Mesh extruded")
mesh.export('./outputs/test.stl')
print("STL exported")
scene = trimesh.Scene(mesh)
with open('./outputs/test.html', "w") as file:
    file.write(trimesh.viewer.scene_to_html(scene))
print("HTML exported")





# Test blocage fichier => NOK
import os
import trimesh
from trimesh import viewer # if not written, error in import
import sys

os.chdir(r'C:\TOOLS\Perso\SVGtag\examples')
svg_path = r'./outputs/shape_ink.svg'
path = trimesh.load_path(svg_path, file_type='svg')
print("Path loaded")
os.remove(svg_path)
print("Deleted svg")
mesh = path.extrude(3)
print("Mesh extruded")
mesh.export('./outputs/test.stl')
print("STL exported")
scene = trimesh.Scene(mesh)
with open('./outputs/test.html', "w") as file:
    file.write(trimesh.viewer.scene_to_html(scene))
print("HTML exported")




















# N'oubliez pas de fermer le fichier log à la fin du script
sys.stdout.close()

# Restaurer la sortie standard à la console
sys.stdout = sys.__stdout__