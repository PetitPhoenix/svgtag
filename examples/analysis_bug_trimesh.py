import trimesh
import numpy as np


def check(mesh, view = False):
    if not (mesh.is_winding_consistent and mesh.is_watertight and mesh.volume > 0):
        print("Volume: ", mesh.is_volume)
        print("Watertight: ", mesh.is_watertight)
        print("Winding: ", mesh.is_winding_consistent)
        trimesh.repair.broken_faces(mesh, color=[255,0,0,255])
        if view == True: mesh.show(smooth=False, viewer='gl', flags={'wireframe': True, 'axis': True})
    else:
        print("All good")

def print_param(path):
    print(path._vertices)
    print(path.length)
    print(path.area)
    print(path.extents)
    print(path.bounds)
    print(path.centroid)
    print(path.vertex_nodes)
    print(path.vertices)
    print(path.obb)
    print(path.identifier)
    
# Charger les contours SVG comme polygones
shape_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\shape.svg')
shape_svg.fill_gaps()
shape_mesh = shape_svg.extrude(3)
check(shape_mesh)
print_param(shape_svg)

shape_ink_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\shape_ink.svg')
shape_ink_mesh = shape_ink_svg.extrude(3)
check(shape_ink_mesh)

print(shape_svg.bounds)
print(shape_ink_svg.bounds)

print(shape_svg._vertices)
print(shape_ink_svg._vertices)

print(shape_svg.centroid)
print(shape_ink_svg.centroid)
print(shape_svg.length)
print(shape_ink_svg.length)
print(shape_svg.area)
print(shape_ink_svg.area)

print(shape_svg.identifier)
print(shape_ink_svg.identifier)

hole_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\hole.svg')
logo_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\logo\\Tetsudau_logo.svg')
text_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\signes\\accidents_01.svg')

shape_svg.fill_gaps()
shape_mesh = shape_svg.extrude(3)
check(shape_mesh)

face_mask = (shape_mesh.visual.face_colors == [255,0,0,255]).all(axis=1)
print(shape_mesh.faces.shape)
print(face_mask.shape)
shape_mesh.update_faces(face_mask)
print(shape_mesh.faces.shape)
mesh.show(smooth=False, viewer='gl', flags={'wireframe': True, 'axis': True})

shape_mesh.fill_holes()
check(shape_mesh)

trimesh.repair.fix_inversion(shape_mesh)
check(shape_mesh)

trimesh.repair.fix_normals(shape_mesh)
check(shape_mesh)

trimesh.repair.stitch(shape_mesh)
check(shape_mesh, view = True)