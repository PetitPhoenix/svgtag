import io
import trimesh
from trimesh import viewer # if not written, error in import

# TODO: batch booleans?
# TODO: proper rotation of cam

def load_svg(svg):
    path = trimesh.load_path(io.StringIO(svg.content), file_type="svg")
    return path

def extrude(path, thickness):
    mesh = path.extrude(thickness)
    if isinstance(mesh, list): mesh = trimesh.boolean.union(mesh)
    return mesh

def extrude_poly(path, thickness):
    # path = path.simplify(tolerance = 0.2)
    poly = path.polygons_full
    path = [trimesh.load_path(p.simplify(tolerance=0.1)) for p in poly]
    if isinstance(path, list):
        mesh = [p.extrude(thickness) for p in path]
    else:
        mesh = path.extrude(thickness)
    if isinstance(mesh, list):
        mesh = trimesh.boolean.union(mesh)
    return mesh

def html(mesh):
    return viewer.scene_to_html(trimesh.Scene(mesh))

def create_scene(meshes, brand=None, full_export=False):
    # Appliquer le matériau
    material = trimesh.visual.material.SimpleMaterial(
        diffuse=[0.8, 0.8, 0.8], ambient=[1, 1, 1], specular=None, glossiness=1
    )
    for i in range(len(meshes)):
        meshes[i].visual.material = material
    
    # Définir les couleurs des faces
    meshes[0].visual.face_colors = [48, 48, 48, 255]
    for i in range(1, len(meshes)):
        meshes[i].visual.face_colors = [248, 248, 241, 255]
    
    # Créer la scène
    scene = trimesh.Scene()
    for i in range(len(meshes)):
        scene.add_geometry(meshes[i])
        
        
    # R = trimesh.transformations.concatenate_matrices(
        
        # trimesh.transformations.rotation_matrix(angle=-np.pi / 3, direction=[1, 0, 0]),
        # trimesh.transformations.rotation_matrix(angle=0*np.pi, direction=[0, 0, 1]),
        # scene.camera_transform, 
    # )
    # R[0:3, 3] = [0, 3 * 75, 3 * 3]
    # scene.camera_transform = R
    # scene.show(viewer='gl', flags={'wireframe': False, 'axis': True})
    return scene

# def batch_booleans(mesh, negatives):
#     # negative = trimesh.Trimesh()
#     for i in range(len(negatives)):
#         mesh = trimesh.boolean.difference([mesh, negatives])
#     return mesh

# def export(mesh, style="html", path=None, name=None):
#     scene = trimesh.Scene(mesh)
#     if style == "scene":
#         data = viewer.scene_to_html(scene)
#         return scene, data
#     elif style == "html":
#         with open(os.path.join(path, name + ".html"), "w") as file:
#             file.write(viewer.scene_to_html(scene))
#         print(f"Scene saved to '{os.path.join(path, name + '.html')}'")
#     elif style == "stl":
#         # trimesh.exchange.stl.export_stl(mesh)
#         mesh.export(os.path.join(path, name + ".stl"))
#         print(f"Mesh saved to '{os.path.join(path, name + '.stl')}'")


if __name__ == "__main__":
    import os
    from svgtag.svgprocess import SVG, read_svg
    
    input_path = '../examples/inputs'
    output_path = '../examples/outputs/mesh'
    
    # Importing path
    tag = SVG(read_svg(os.path.join(input_path, 'shape.svg')))
    path = load_svg(tag)
    path.show()
    
    # Exporting model
    mesh = extrude(path, thickness=3)
    mesh.export(os.path.join(output_path, 'mesh.stl'))
    
    # Exporting view in html
    with open(os.path.join(output_path, 'mesh.html'), "w") as file:
        file.write(html(mesh))
