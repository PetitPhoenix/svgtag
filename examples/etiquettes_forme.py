from shape2svg import shape_svg
from text2svg import text_svg, generate_svg, flip
from fontTools.ttLib import TTFont
import os
os.environ['path'] += r';C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin'
import cairosvg

def main():
    # Paramètres de la forme
    width_mm = 80
    height_mm = 35
    thk = 1
    shape = 'circle'  # 'rectangle', 'triangle', ou 'circle'
    transform = '' # '', 'flip' 
    phi = 6
    
    loc_vis = [0, 0, width_mm + height_mm / 2 if phi > 0 else width_mm, height_mm]
    
    svg_shape = shape_svg(width_mm, height_mm, thk, shape, phi)
    
    if transform == 'flip':
        svg_shape = flip(svg_shape, loc_vis[2])
    
    output_folder = "/outputs"
    os.makedirs(output_folder, exist_ok=True)

    
    # Génération des noms de fichiers
    nom_fichier = "shape"
    generate_svg(svg_shape, os.path.join('./outputs', nom_fichier + '.svg'), loc_vis)          
    cairosvg.svg2png(url=os.path.join('./outputs', nom_fichier + '.svg'), write_to=os.path.join('./outputs', nom_fichier + '.png'))#, output_width=1920, output_height=1080)

    # from svglib.svglib import svg2rlg
    # from reportlab.graphics import renderPM
    # drawing = svg2rlg(os.path.join('./outputs', nom_fichier + '.svg'))
    # renderPM.drawToFile(drawing, os.path.join('./outputs', nom_fichier + '.png'), fmt="PNG")

if __name__ == "__main__":
    main()