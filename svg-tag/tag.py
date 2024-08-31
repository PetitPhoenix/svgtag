import os
from shape2svg import shape_svg
from text2svg import text_svg# , flip

def tag(text, output):
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
    font_size = None
    interline_ratio = 0.8
    ratio_print = 0.9
    
    # Reduce the area not to avoid touching the borders
    width_txt = zoneWidth_mm * ratio_print
    height_txt = zoneHeight_mm * ratio_print
    x_mm = 0
    y_mm = 0
    x_txt = x_mm + (zoneWidth_mm - width_txt) / 2
    y_txt = y_mm + (zoneHeight_mm - height_txt) / 2
    
    # Generate the 2 SVG
    svg_text = text_svg(text, font_path, font_size, width_txt - x_mm, height_txt - y_mm, x_txt, y_txt, interline_ratio = interline_ratio)
    svg_shape = shape_svg(zoneWidth_mm, zoneHeight_mm, thk, shape, phi)
    
    # if transform == 'flip':
    #     x_txt = 0
    #     svg_shape = flip(svg_shape, loc_vis[2])
    
    svg = svg_shape
    svg.add_svg(svg_text)
    svg.add_element("rect", {"x": x_txt, "y": y_txt, "width": width_txt - x_mm, "height": height_txt - y_mm, "stroke": "black", "fill": "transparent", "stroke-width": 0.1 }, {"translate": (0, 0), "scale": 1})
    svg.unit = 'mm'

    svg.generate_svg_file(output)

def main():
    text = "Impression d'une étiquette"
    
    output_path = '../examples/outputs'
    output_file = 'tag'
    output = os.path.join(output_path, output_file + '.svg')
    tag(text, output)
            
if __name__ == "__main__":
    main()
