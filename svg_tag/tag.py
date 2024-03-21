from shape2svg import shape_svg
from text2svg import text_svg, generate_svg, flip
from fontTools.ttLib import TTFont

def main():
    output_file = 'tag.svg'
    
    # Paramètres de la forme
    width_mm = 80
    height_mm = 35
    thk = 1
    shape = 'circle'  # 'rectangle', 'triangle', ou 'circle'
    transform = 'flip' # '', 'flip' 
    phi = 6
    x_mm = height_mm / 2 if phi > 0 else 0
    y_mm = 0
    
    # Paramètres du texte
    text = "Impression d'une étiquette"
    font_path = './static/fonts/impact.ttf'
    font_size = 30
    # print(f'Taille de police en mm: {(font_size / 72) * 25.4:.02f}')
    
    ratio_print = 0.9
    interline_ratio = 0.8
    width_txt = width_mm * ratio_print
    height_txt = height_mm * ratio_print
    x_txt = x_mm + (width_mm - width_txt) / 2
    y_txt = y_mm + (height_mm - height_txt) / 2
    
    loc_vis = [0, 0, width_mm + height_mm / 2 if phi > 0 else width_mm, height_mm]
    
    # Préparation des paramètres visuels pour le texte
    svg_shape = shape_svg(width_mm, height_mm, thk, shape, phi)
    if transform == 'flip':
        x_txt = 0
        svg_shape = flip(svg_shape, loc_vis[2])
    svg_text = text_svg(text, font_path, font_size, width_txt, height_txt, x_txt, y_txt, interline_ratio, n = 2)
    
    generate_svg([svg_text, svg_shape], output_file, loc_vis)

if __name__ == "__main__":
    main()