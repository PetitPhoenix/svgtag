import sys
sys.path.append(r'C:\TOOLS\Perso\svg-tag\svg-tag')

from shape2svg import shape_svg
from text2svg_self import text_svg, generate_svg, flip
from fontTools.ttLib import TTFont
import os
os.environ['path'] += r';C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin'
# import cairosvg



def main():
    # Paramètres de la forme
    width_mm = 80
    height_mm = 35
    thk = 1
    shape = 'circle'  # 'rectangle', 'triangle', ou 'circle'
    transform = '' # '', 'flip' 
    phi = 6
    x_mm = height_mm / 2 if phi > 0 else 0
    y_mm = 0
    
    # Paramètres du texte
    font_path = './static/fonts/impact.ttf'
    font_size = 60
    
    ratio_print = 0.9
    interline_ratio = 0.8
    width_txt = width_mm * ratio_print
    height_txt = height_mm * ratio_print
    x_txt = x_mm + (width_mm - width_txt) / 2
    y_txt = y_mm + (height_mm - height_txt) / 2
    
    loc_vis = [0, 0, width_mm + height_mm / 2 if phi > 0 else width_mm, height_mm]
    
    # Préparation des paramètres visuels pour le texte
    font = TTFont(font_path)
    unitsPerEm = font['head'].unitsPerEm
    scale = (font_size) / (72 * unitsPerEm) * 25.4
    svg_shape = shape_svg(width_mm, height_mm, thk, shape, phi)
    
    if transform == 'flip':
        x_txt = 0
        svg_shape = flip(svg_shape, loc_vis[2])
    
    # Définition des catégories et de leurs étiquettes
    etiquettes = {
        "Basique": ["Ça va ?", 
                    "Ok", 
                    "Quelle pression ?", 
                    "Mi-pression", 
                    "Réserve", 
                    "Attends", 
                    "Ralentis", 
                    "Attention au milieu", 
                    "Oreilles"],
        "Accidents": ["Ça va pas !", 
                      "Essouflé", 
                      "Panne d'air", 
                      "Froid", 
                      "Narcose", 
                      "Changement de gaz", 
                      "Run-time de secours", 
                      "Dévidoir", 
                      "Profondeur max?"],
        "Autonomie": ["Bateau", 
                      "Paliers", 
                      "Parachute", 
                      "Ordinateur", 
                      "Mètres", 
                      "Minutes", 
                      "3m 6m 9m", 
                      "1' 3' 5'"],
        "Stabilisation": ["Purge", 
                          "Gonfle", 
                          "Stabilise-toi", 
                          "Purge lente", 
                          "Purge haute", 
                          "Purge basse", 
                          "Monte", 
                          "Descend"],
        "Ventilation": ["Apnée", 
                        "Inspiratoire", 
                        "Expiratoire", 
                        "Lâcher embout", 
                        "Reprise embout", 
                        "Souffle", 
                        "Inspire", 
                        "Expire"]
        }
    
    
    output_folder = "/outputs"
    os.makedirs(output_folder, exist_ok=True)

    
    # # Initialisation d'une liste vide pour stocker les données
    data = []
    
    generate_svg(svg_shape, os.path.join('./outputs', 'shape.svg'), loc_vis)
    
    # Génération des noms de fichiers
    for categorie, etiquettes in etiquettes.items():
        for index, etiquette in enumerate(etiquettes, start=1):
            nom_fichier = f"{categorie.lower()}_{index:02d}"
            svg_text = text_svg(etiquette, font, font_size, width_txt, height_txt, x_txt, y_txt, scale, interline_ratio)
            generate_svg([svg_text], os.path.join('./outputs', nom_fichier + '.svg'), loc_vis)
            #cairosvg.svg2png(url=os.path.join('./outputs', nom_fichier + '.svg'), write_to=os.path.join('./outputs', nom_fichier + '.png'))#, output_width=1920, output_height=1080)

            # from svglib.svglib import svg2rlg
            # from reportlab.graphics import renderPM
            # drawing = svg2rlg(os.path.join('./outputs', nom_fichier + '.svg'))
            # renderPM.drawToFile(drawing, os.path.join('./outputs', nom_fichier + '.png'), fmt="PNG")
            data.append((categorie, etiquette, nom_fichier))
    
    print(data)

if __name__ == "__main__":
    main()