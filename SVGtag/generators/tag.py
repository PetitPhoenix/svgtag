import os
import trimesh
import numpy as np

from ..shape2svg import shape_svg
from ..text2svg import text_svg
from ..SVGprocess import SVG

def tag(text, font_path, length, height, phi=None, shape='circle', outline=False):
    # Shape parameters [mm]
    zoneWidth_mm = length
    zoneHeight_mm = height
    thk = 0.1
    
    # Text parameters
    font_size = None
    interline_ratio = 0.8
    ratio_print = 0.9
    padding = 5
    border = 2
    
    # Reduce the area not to avoid touching the borders
    if padding == None:
        width_txt = zoneWidth_mm * ratio_print
        height_txt = zoneHeight_mm * ratio_print
    else:
        width_txt = zoneWidth_mm - 2 * padding
        height_txt = zoneHeight_mm - 2 * padding
        
    x_mm = 0
    y_mm = 0
    x_txt = x_mm + (zoneWidth_mm - width_txt) / 2
    y_txt = y_mm + (zoneHeight_mm - height_txt) / 2
    
    if shape != None:
        svg = shape_svg(zoneWidth_mm, zoneHeight_mm, thk, shape, phi)
    else:
        svg = SVG('', ppi=96)
    
    if text:
        svg.add_svg(text_svg(text, font_path, font_size, width_txt - x_mm, height_txt - y_mm, x_txt, y_txt, interline_ratio = interline_ratio))
    
    if outline == True:
        svg.add_element("rect", {"x": x_txt, "y": y_txt, "width": width_txt - x_mm, "height": height_txt - y_mm, "stroke": "black", "fill": "transparent", "stroke-width": 0.1 }, {"translate": (0, 0), "scale": 1})
        if border != None:
            svg.add_element("rect", {"x": x_txt - border, "y": y_txt - border, "width": width_txt + 2 * border - x_mm, "height": height_txt + 2 * border - y_mm, "stroke": "black", "fill": "transparent", "stroke-width": 0.1 }, {"translate": (0, 0), "scale": 1})
    
    svg.height = zoneHeight_mm
    if phi == 0:
        svg.width = zoneWidth_mm
        svg.viewBox = [0, 0, zoneWidth_mm, zoneHeight_mm]
    else:
        svg.width = zoneWidth_mm + zoneHeight_mm / 2
        svg.viewBox = [- zoneHeight_mm / 2 , 0, zoneWidth_mm + zoneHeight_mm / 2, zoneHeight_mm]
    svg.unit = 'mm'
    # svg.generate_svg_file(output)
    return svg

def svg2stl(shape, thickness, output_path, side_A, side_B = None, brand = None):
    with open(shape, 'rb') as file:
        shape_svg = trimesh.load_path(file, file_type='svg')
    shape_mesh = shape_svg.extrude(thickness)
    
    with open(side_A, 'rb') as file:
        side_A_svg = trimesh.load_path(file, file_type='svg')
    side_A_mesh = side_A_svg.extrude(thickness/6)
    side_A_mesh = trimesh.boolean.union(side_A_mesh)
    negative = side_A_mesh.copy()
    
    
    if side_B :
        with open(side_B, 'rb') as file:
            side_B_svg = trimesh.load_path(file, file_type='svg')
        side_B_mesh = side_B_svg.extrude(thickness/6)
        side_B_mesh = trimesh.boolean.union(side_B_mesh)
        # side_B_mesh = side_B_mesh.apply_transform(trimesh.transformations.rotation_matrix(angle = np.pi, direction = [0, 1, 0]))
        side_B_mesh = side_B_mesh.apply_transform(trimesh.transformations.rotation_matrix(angle = np.pi, direction = [1, 0, 0]))

        if brand == True:
            side_B_mesh = side_B_mesh.apply_transform(trimesh.transformations.scale_and_translate(scale = [0.4, 0.4, 1], translate = [0.4*shape_mesh.extents[0], 0.4*shape_mesh.extents[1], thickness]))#[0.6*(shape_mesh.extents[0] - side_B_mesh.extents[0]), 0.6*side_B_mesh.extents[1], thickness]))
        else:
            side_B_mesh = side_B_mesh.apply_transform(trimesh.transformations.scale_and_translate(scale = [1, 1, 1], translate = [0, shape_mesh.extents[1], thickness]))

        negative = negative.union(side_B_mesh)

    
    mesh = trimesh.boolean.difference([shape_mesh, negative])
    
    material = trimesh.visual.material.SimpleMaterial(diffuse=[0.8, 0.8, 0.8], ambient=[1, 1, 1], specular=None, glossiness=1)# PBRMaterial(name="PLA")
    shape_mesh.visual.material = material
    side_A_mesh.visual.material = material
    if side_B :
        side_B_mesh.visual.material = material
    mesh.visual.material = material

    # shape_mesh.visual.face_colors = [45, 250, 250, 255]
    side_A_mesh.visual.face_colors = [248, 248, 241, 255]
    if side_B :
        side_B_mesh.visual.face_colors = [248, 248, 241, 255]
    mesh.visual.face_colors = [48, 48, 48, 255]
    
    scene = trimesh.Scene()
    scene.add_geometry([mesh, side_A_mesh])
    if side_B :
        scene.add_geometry(side_B_mesh)
    
    R = trimesh.transformations.concatenate_matrices(trimesh.transformations.rotation_matrix(angle = -np.pi / 3, direction = [1, 0, 0]), 
                                                     trimesh.transformations.rotation_matrix(angle = np.pi, direction = [0, 0, 1])
                                                     )
    R[0:3, 3] = [0, 3 * 75, 3 * 3]
    scene.camera_transform = R
    # scene.show(viewer='gl', flags={'wireframe': False, 'axis': True})

    mesh.export(os.path.join(output_path, 'mesh.stl'))
    side_A_mesh.export(os.path.join(output_path, 'side_A.stl'))
    if side_B :
        side_B_mesh.export(os.path.join(output_path, 'side_B.stl'))
    print(f"STL saved at {os.path.abspath(output_path)}")

    return scene

def tag_3D(filename, input_path, output_path):
    with open(os.path.join(input_path, 'shape.svg'), 'rb') as file:
        shape_svg = trimesh.load_path(file, file_type='svg')
    # shape_svg = trimesh.load_path(os.path.join(input_path, 'shape.svg'))
    shape_mesh = shape_svg.extrude(3)
    
    # with open(os.path.join(input_path, 'hole.svg'), 'rb') as file:
    #     hole_svg = trimesh.load_path(file, file_type='svg')
    # # hole_svg = trimesh.load_path(os.path.join(input_path, 'hole.svg'))
    # hole_mesh = hole_svg.extrude(3)
    
    with open(os.path.join(input_path, 'Tetsudau_logo.svg'), 'rb') as file:
        logo_svg = trimesh.load_path(file, file_type='svg')
    # logo_svg = trimesh.load_path(os.path.join(input_path, 'Tetsudau_logo.svg'))
    logo_mesh = logo_svg.extrude(0.5)
    logo_mesh = trimesh.boolean.union(logo_mesh)
    logo_mesh = logo_mesh.apply_transform(trimesh.transformations.rotation_matrix(angle = np.pi, direction = [0, 1, 0]))
    logo_mesh = logo_mesh.apply_transform(trimesh.transformations.scale_and_translate(scale = [0.7, 0.7, 1], translate = [75, 10, 3]))
    
    with open(os.path.join(input_path, f'{filename}.svg'), 'rb') as file:
        text_svg = trimesh.load_path(file, file_type='svg')
    # text_svg = trimesh.load_path(os.path.join(input_path, f'{filename}.svg'))
    text_mesh = text_svg.extrude(2)
    text_mesh = trimesh.boolean.union(text_mesh)
    
    scene = trimesh.Scene()
    scene.add_geometry([shape_mesh, logo_mesh, text_mesh])
    # scene.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    
    negative = text_mesh.copy()
    
    tag_mesh = trimesh.boolean.difference([shape_mesh, negative])
    
    # negative.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    # tag_mesh.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    # tag_mesh.show(viewer='gl')
    
    logo_mesh.export(os.path.join(output_path, '01_logo.stl'))
    tag_mesh.export(os.path.join(output_path, f'{filename}_0.stl'))
    text_mesh.export(os.path.join(output_path, f'{filename}_1.stl'))
    print(f"STL saved at {os.path.abspath(os.path.join(output_path, f'{filename}_X.stl'))}")

def tag_3D_RV(recto, verso, input_path, output_path):
    with open(os.path.join(input_path, 'shape.svg'), 'rb') as file:
        shape_svg = trimesh.load_path(file, file_type='svg')
    # shape_svg = trimesh.load_path(os.path.join(input_path, 'shape.svg'))
    shape_mesh = shape_svg.extrude(3)
    
    with open(os.path.join(input_path, 'hole.svg'), 'rb') as file:
        hole_svg = trimesh.load_path(file, file_type='svg')
    # hole_svg = trimesh.load_path(os.path.join(input_path, 'hole.svg'))
    hole_mesh = hole_svg.extrude(3)
    
    with open(os.path.join(input_path, f'{recto}.svg'), 'rb') as file:
        recto_svg = trimesh.load_path(file, file_type='svg')
    # recto_svg = trimesh.load_path(os.path.join(input_path, f'{recto}.svg'))
    recto_mesh = recto_svg.extrude(1)
    recto_mesh = trimesh.boolean.union(recto_mesh)
    
    with open(os.path.join(input_path, f'{recto}.svg'), 'rb') as file:
        verso_svg = trimesh.load_path(file, file_type='svg')
    # verso_svg = trimesh.load_path(os.path.join(input_path, f'{verso}.svg'))
    verso_mesh = verso_svg.extrude(1)
    verso_mesh = trimesh.boolean.union(verso_mesh)
    verso_mesh = verso_mesh.apply_transform(trimesh.transformations.rotation_matrix(angle = np.pi, direction = [1, 0, 0]))
    verso_mesh = verso_mesh.apply_transform(trimesh.transformations.scale_and_translate(scale = [1, 1, 1], translate = [0, 35, 3]))
    
    scene = trimesh.Scene()
    scene.add_geometry([shape_mesh, recto_mesh, verso_mesh, hole_mesh])
    # scene.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    
    negative = hole_mesh.copy()
    negative = negative.union(recto_mesh)
    negative = negative.union(verso_mesh)
    tag_mesh = trimesh.boolean.difference([shape_mesh, negative])
    
    # negative.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    # tag_mesh.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    # tag_mesh.show(viewer='gl')
    if recto.split("_", 1)[0] == verso.split("_", 1)[0]:
        outputname = recto + '-' + verso.split("_", 1)[-1]
    elif recto.split("_", 1)[-1] == verso.split("_", 1)[-1]:
        outputname = recto.split("_", 1)[0] + '-' + verso
    tag_mesh.export(os.path.join(output_path, f'{outputname}_0.stl'))
    recto_mesh.export(os.path.join(output_path, f'{recto}_1.stl'))
    verso_mesh.export(os.path.join(output_path, f'{verso}_1.stl'))
    print(f"STL saved at {os.path.abspath(os.path.join(output_path, f'{outputname}_X.stl'))}")