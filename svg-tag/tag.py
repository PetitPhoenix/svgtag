import os
import trimesh
import numpy as np

from shape2svg import shape_svg
from text2svg import text_svg# , flip
from SVGprocess import SVG

def tag(text, output, include_shape = True, outline = False):
    # Shape parameters [mm]
    shape = 'circle'  # 'rectangle', 'triangle', ou 'circle'
    # transform = '' # '', 'flip' 
    phi = 5
    zoneWidth_mm = 80
    zoneHeight_mm = 35
    thk = 1
    
    # loc_vis = [0, 0, zoneWidth_mm + zoneHeight_mm / 2 if phi > 0 else zoneWidth_mm, zoneHeight_mm]
    
    # Text parameters
    font_path = '../static/fonts/Impact/impact.ttf'
    font_size = 60
    interline_ratio = 0.8
    ratio_print = 0.9
    
    # Reduce the area not to avoid touching the borders
    width_txt = zoneWidth_mm * ratio_print
    height_txt = zoneHeight_mm * ratio_print
    x_mm = 0
    y_mm = 0
    x_txt = x_mm + (zoneWidth_mm - width_txt) / 2
    y_txt = y_mm + (zoneHeight_mm - height_txt) / 2
    
    # if transform == 'flip':
    #     x_txt = 0
    #     svg_shape = flip(svg_shape, loc_vis[2])
    
    if include_shape == True:
        svg = shape_svg(zoneWidth_mm, zoneHeight_mm, thk, shape, phi)
    else:
        svg = SVG('', ppi=96)
    
    if text:
        svg.add_svg(text_svg(text, font_path, font_size, width_txt - x_mm, height_txt - y_mm, x_txt, y_txt, interline_ratio = interline_ratio))
    
    if outline == True:
        svg.add_element("rect", {"x": x_txt, "y": y_txt, "width": width_txt - x_mm, "height": height_txt - y_mm, "stroke": "black", "fill": "transparent", "stroke-width": 0.1 }, {"translate": (0, 0), "scale": 1})
    
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
    shape_svg = trimesh.load_path(os.path.join(input_path, 'shape_ink.svg'))
    shape_mesh = shape_svg.extrude(3)
    
    hole_svg = trimesh.load_path(os.path.join(input_path, 'hole_ink.svg'))
    hole_mesh = hole_svg.extrude(3)
    
    logo_svg = trimesh.load_path('../examples/static/images/Tetsudau_logo.svg')
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
    shape_svg = trimesh.load_path(os.path.join(input_path, 'shape_ink.svg'))
    shape_mesh = shape_svg.extrude(3)
    
    hole_svg = trimesh.load_path(os.path.join(input_path, 'hole_ink.svg'))
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

def main():
    text1 = "Impression d'une étiquette"
    text2 = "Recto / Verso"

    output_path = '../examples/outputs'
    tag("", os.path.join(output_path, 'tag_shp.svg'), include_shape = True, outline = True)
    tag(text1, os.path.join(output_path, 'tag1.svg'), include_shape = True, outline = True)
    tag(text1, os.path.join(output_path, 'tag_txt1.svg'), include_shape = False, outline = False)
    tag(text2, os.path.join(output_path, 'tag2.svg'), include_shape = True, outline = True)
    tag(text2, os.path.join(output_path, 'tag_txt2.svg'), include_shape = False, outline = False)
    
    input_path = output_path
    #tag_3D('tag_txt1, input_path, output_path)
    tag_3D_RV('tag_txt1', 'tag_txt2', input_path, output_path)

if __name__ == "__main__":
    main()
