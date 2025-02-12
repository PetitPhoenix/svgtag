import trimesh
import sys

log_file_path = 'analysis_bug_trimesh.log'
sys.stdout = open(log_file_path, 'w')

def check(mesh, view = False):
    print('Performing checks:')
    if not (mesh.is_winding_consistent and mesh.is_watertight and mesh.volume > 0):
        print("Volume: ", mesh.is_volume)
        print("Watertight: ", mesh.is_watertight)
        print("Winding: ", mesh.is_winding_consistent)
        trimesh.repair.broken_faces(mesh, color=[255,0,0,255])
        if view == True: mesh.show(smooth=False, viewer='gl', flags={'wireframe': True, 'axis': True})
    else:
        print("All good")

def print_param(path):
    print('Printing parameters:')
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
print('Working on shape.svg')
shape_svg = trimesh.load_path(r'./inputs/shape.svg')
shape_svg.fill_gaps(distance=0.1)
shape_mesh = shape_svg.extrude(3)
check(shape_mesh)
# print_param(shape_svg)

print('Working on shape_ink.svg')
shape_ink_svg = trimesh.load_path(r'./inputs/shape_ink.svg')
shape_ink_mesh = shape_ink_svg.extrude(3)
check(shape_ink_mesh)
# print_param(shape_ink_svg)
print('\n')

print('Comparison:')
print('bounds:')
print(shape_svg.bounds)
print('-----===-----')
print(shape_ink_svg.bounds)
print('\n')

print('vertices:')
print(shape_svg._vertices)
print('-----===-----')
print(shape_ink_svg._vertices)
print('\n')

print('centroid:')
print(shape_svg.centroid)
print('-----===-----')
print(shape_ink_svg.centroid)
print('\n')

print('length:')
print(shape_svg.length)
print('-----===-----')
print(shape_ink_svg.length)
print('\n')

print('area:')
print(shape_svg.area)
print('-----===-----')
print(shape_ink_svg.area)
print('\n')

print('identifier:')
print(shape_svg.identifier)
print('-----===-----')
print(shape_ink_svg.identifier)
print('\n')


# N'oubliez pas de fermer le fichier log à la fin du script
sys.stdout.close()

# Restaurer la sortie standard à la console
sys.stdout = sys.__stdout__

print(f"Analysis completed. Details can be found in '{log_file_path}'")



# hole_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\hole.svg')
# logo_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\logo\\Tetsudau_logo.svg')
# text_svg = trimesh.load_path('C:\\TOOLS\\Perso\\etiquettes\\inputs\\signes\\accidents_01.svg')

# shape_svg.fill_gaps()
# shape_mesh = shape_svg.extrude(3)
# check(shape_mesh)

# face_mask = (shape_mesh.visual.face_colors == [255,0,0,255]).all(axis=1)
# print(shape_mesh.faces.shape)
# print(face_mask.shape)
# shape_mesh.update_faces(face_mask)
# print(shape_mesh.faces.shape)
# mesh.show(smooth=False, viewer='gl', flags={'wireframe': True, 'axis': True})

# shape_mesh.fill_holes()
# check(shape_mesh)

# trimesh.repair.fix_inversion(shape_mesh)
# check(shape_mesh)

# trimesh.repair.fix_normals(shape_mesh)
# check(shape_mesh)

# trimesh.repair.stitch(shape_mesh)
# check(shape_mesh, view = True)