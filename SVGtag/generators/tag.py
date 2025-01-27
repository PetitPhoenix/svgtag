import os
import trimesh
import numpy as np

from ..shape2svg import shape_svg
from ..text2svg import text_svg
from ..SVGprocess import SVG

def tag(text, font_path, length, height, output, phi=None, shape='circle', outline=False):
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
    svg.generate_svg_file(output)

def tag_3D(filename, input_path, output_path):
    shape_svg = trimesh.load_path(os.path.join(input_path, 'shape.svg'))
    shape_mesh = shape_svg.extrude(3)
    
    hole_svg = trimesh.load_path(os.path.join(input_path, 'hole.svg'))
    hole_mesh = hole_svg.extrude(3)
    
    logo_svg = trimesh.load_path(os.path.join(input_path, 'Tetsudau_logo.svg'))
    logo_mesh = logo_svg.extrude(0.5)
    logo_mesh = trimesh.boolean.union(logo_mesh)
    logo_mesh = logo_mesh.apply_transform(trimesh.transformations.rotation_matrix(angle = np.pi, direction = [0, 1, 0]))
    logo_mesh = logo_mesh.apply_transform(trimesh.transformations.scale_and_translate(scale = [0.7, 0.7, 1], translate = [75, 10, 3]))
    
    text_svg = trimesh.load_path(os.path.join(input_path, f'{filename}.svg'))
    text_mesh = text_svg.extrude(2)
    text_mesh = trimesh.boolean.union(text_mesh)
    
    scene = trimesh.Scene()
    scene.add_geometry([shape_mesh, logo_mesh, text_mesh, hole_mesh])
    # scene.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    
    negative = text_mesh.copy()
    negative = negative.union(logo_mesh)
    negative = negative.union(hole_mesh)
    tag_mesh = trimesh.boolean.difference([shape_mesh, negative])
    
    # negative.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    # tag_mesh.show(viewer='gl', flags={'wireframe': True, 'axis': True})
    # tag_mesh.show(viewer='gl')
    
    logo_mesh.export(os.path.join(output_path, '01_logo.stl'))
    tag_mesh.export(os.path.join(output_path, f'{filename}_0.stl'))
    text_mesh.export(os.path.join(output_path, f'{filename}_1.stl'))
    print(f"STL saved at {os.path.abspath(os.path.join(output_path, f'{filename}_X.stl'))}")

def tag_3D_RV(recto, verso, input_path, output_path):
    shape_svg = trimesh.load_path(os.path.join(input_path, 'shape.svg'))
    shape_mesh = shape_svg.extrude(3)
    
    hole_svg = trimesh.load_path(os.path.join(input_path, 'hole.svg'))
    hole_mesh = hole_svg.extrude(3)
    
    recto_svg = trimesh.load_path(os.path.join(input_path, f'{recto}.svg'))
    recto_mesh = recto_svg.extrude(1)
    recto_mesh = trimesh.boolean.union(recto_mesh)
    
    verso_svg = trimesh.load_path(os.path.join(input_path, f'{verso}.svg'))
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