import os
from shape2svg import shape_svg
from text2svg import text_svg, flip

def main():
    output_path = '../examples/outputs'
    output_file = 'tag.svg'
    
    # Paramètres de la forme
    width_mm = 80
    height_mm = 35
    thk = 1
    shape = 'circle'  # 'rectangle', 'triangle', ou 'circle'
    transform = '' # '', 'flip' 
    phi = 6
    loc_vis = [0, 0, width_mm + height_mm / 2 if phi > 0 else width_mm, height_mm]

    x_mm = height_mm / 2 if phi > 0 else 0
    y_mm = 0
    
    # Paramètres du texte
    text = "Impression d'une étiquette"
    font_path = '../static/fonts/Impact/impact.ttf'
    font_size = 30
    ratio_print = 0.9
    interline_ratio = 0.8
    width_txt = width_mm * ratio_print
    height_txt = height_mm * ratio_print
    x_txt = x_mm + (width_mm - width_txt) / 2
    y_txt = y_mm + (height_mm - height_txt) / 2
    
    # Création des SVG
    svg_shape = shape_svg(width_mm, height_mm, thk, shape, phi)
    
    if transform == 'flip':
        x_txt = 0
        svg_shape = flip(svg_shape, loc_vis[2])
        
    svg_text = text_svg(text, font_path, font_size, width_txt, height_txt, x_txt, y_txt, interline_ratio, n=2)
    
    # Crée une instance SVG et y ajoute les éléments de forme et de texte
    svg = svg_text
    svg.add_svg(svg_shape)
    svg.unit = 'mm'
    svg.width = width_mm
    svg.height = height_mm
    svg.viewBox = [0, 0, width_mm + height_mm / 2 if phi > 0 else width_mm, height_mm]
    svg.update_svg_content()
    svg.generate_svg_file(os.path.join(output_path, output_file))

if __name__ == "__main__":
    main()
