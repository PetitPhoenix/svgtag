from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
import os
import math

class ContourPen(BasePen):
    def __init__(self, glyphSet):
        BasePen.__init__(self, glyphSet)
        self.points = []

    def _moveTo(self, p):
        self.points.append(p)

    def _lineTo(self, p):
        self.points.append(p)

    def _curveToOne(self, p1, p2, p3):
        self.points.extend([p1, p2, p3])

    def _closePath(self):
        pass

    def _endPath(self):
        pass

def calculate_text_width(text, font):
    """
    Computes the width of a text based on a specified font.
    """
    glyphset = font.getGlyphSet()
    kerning_table = font['kern'].kernTables[0].kernTable if 'kern' in font else {}
    text_width = 0
    previous_glyph_name = None
    for char in text:
        glyph_name = font.getBestCmap()[ord(char)]
        glyph = glyphset[glyph_name]
        kerning = 0
        if previous_glyph_name:
            pair = (previous_glyph_name, glyph_name)
            kerning = kerning_table.get(pair, 0)
        text_width += glyph.width + kerning
        previous_glyph_name = glyph_name
    return text_width

def calculate_text_height(text, font):
    """
    Computes the height of a text based on a specified font.
    """
    glyphset = font.getGlyphSet()
    max_ascent = 0
    min_descent = 0
    
    for char in text:
        glyph_name = font.getBestCmap()[ord(char)]
        if glyph_name in glyphset:
            glyph = glyphset[glyph_name]
            pen = ContourPen(glyphset)
            glyph.draw(pen)
            y_points = [point[1] for point in pen.points]
            if y_points:  # Vérifiez que la liste n'est pas vide
                max_ascent = max(max_ascent, max(y_points))
                min_descent = min(min_descent, min(y_points))
    
    text_height = max_ascent - min_descent
    return text_height, max_ascent, min_descent

def calculate_interline(font, scale, interline_ratio):
    """
    Compute the specified spacing between two lines.
    """
    ascent = font['hhea'].ascent * scale
    descent = font['hhea'].descent * scale
    line_gap = font['hhea'].lineGap * scale
    return (ascent - descent + line_gap) * interline_ratio

def calculate_line_metrics(text, font, scale):
    """
    Compute the metrics for a line of text.
    """
    text_width = calculate_text_width(text, font)
    text_height, max_ascent, min_descent = calculate_text_height(text, font)
    
    return {
        "width": text_width * scale,
        "height": (max_ascent - min_descent) * scale,
        "ascent": max_ascent * scale,
        "descent": min_descent * scale
    }

def draw_text_line(text, x, y, font, font_size, scale):
    """
    Draw the SVG of a text.
    
    Args:
        text: A list of SVG element strings or a single SVG element string.
        x, y: position for the text.
        font_size: font size
        scale: conversion from PerEm to mm.
    """
    glyphset = font.getGlyphSet()
    kerning_table = font['kern'].kernTables[0].kernTable if 'kern' in font else {}
    svg_paths = []
    previous_glyph_name = None
    for char in text:
        glyph_name = font.getBestCmap()[ord(char)]
        if glyph_name in glyphset:
            glyph = glyphset[glyph_name]
            kerning = 0
            if previous_glyph_name:
                pair = (previous_glyph_name, glyph_name)
                kerning = kerning_table.get(pair, 0) * scale if kerning_table and pair in kerning_table else 0
            x += kerning
            previous_glyph_name = glyph_name
            pen = SVGPathPen(glyphset)
            tpen = TransformPen(pen, (scale, 0, 0, -scale, x, y))
            glyph.draw(tpen)
            path_data = pen.getCommands()
            svg_paths.append(f'<path d="{path_data}"/>')
            x += glyph.width * scale
    return svg_paths

def split_text(text, n):
    """
    Split the text in several (n) lines.
    """
    words = text.split()
    # Si le texte doit être sur une seule ligne ou si le nombre de mots est inférieur au nombre de lignes souhaitées
    if n == 1 or len(words) < n:
        return [text]
    
    # Calculer la longueur approximative des lignes
    avg = len(words) // n
    lines = []
    start = 0
    for i in range(n - 1):  # Diviser en n-1 lignes pour s'assurer que tous les mots sont inclus
        end = start + avg
        lines.append(' '.join(words[start:end]))
        start = end
    
    # Ajouter le reste des mots à la dernière ligne
    lines.append(' '.join(words[start:]))
    return lines

def shape_text(text, font, font_size, zone_width, zone_height, scale, interline_ratio = 0.8, n = []):
    """
    Defines the shape of the text (number of lines, reduces font size).
    """
    unitsPerEm = font['head'].unitsPerEm
    line_metrics = calculate_line_metrics(text, font, scale)
    interline = calculate_interline(font, scale, interline_ratio)
    aspect_ratio = zone_width / zone_height
    if n ==[]: n = max(1, math.floor((line_metrics['width'] / aspect_ratio + interline) / (line_metrics['height'] + interline)))
    if line_metrics['width'] > zone_width:
        text_lines = split_text(text, n)
    else:
        text_lines = [text]
    
    line_metrics = [calculate_line_metrics(line, font, scale) for line in text_lines]
    total_height = line_metrics[0]['ascent'] + (n - 1) * interline - line_metrics[-1]['descent']
    total_width = line_metrics[0]['width']
    
    while total_height > zone_height or total_width > zone_width:
        font_size -= 1
        scale = font_size / (72 * unitsPerEm) * 25.4
        line_metrics = calculate_line_metrics(text, font, scale)
        interline = calculate_interline(font, scale, interline_ratio)
        line_metrics = [calculate_line_metrics(line, font, scale) for line in text_lines]
        if len(text_lines) > 1:
            total_height = line_metrics[0]['ascent'] + (n - 1) * interline - line_metrics[-1]['descent']
        else:
            total_height = line_metrics[0]['height']
        total_width = line_metrics[0]['width']
    return text_lines, n, font_size, scale

def text_svg(text, font_path, font_size, zone_width, zone_height, x0, y0, interline_ratio = 0.8, n = []):
    """
    General procedure that tries to fit the text in a dedicated area.
    """
    if not isinstance(text, str):
        text = str(text)
    if font_size == None:
        font_size = 100
    
    font = TTFont(font_path)
    unitsPerEm = font['head'].unitsPerEm
    scale = font_size / (72 * unitsPerEm) * 25.4 # Dans le cas d'un travail en mm, if px: (font_size * dpi) / (72 * unitsPerEm)
    
    svg_elements = []   
    text_lines, n, font_size, scale = shape_text(text, font, font_size, zone_width, zone_height, scale, interline_ratio, n)
    interline = calculate_interline(font, scale, interline_ratio)
    line_metrics = [calculate_line_metrics(line, font, scale) for line in text_lines]
    if len(text_lines) > 1:
        total_height = line_metrics[0]['ascent'] + (n - 1) * interline - line_metrics[-1]['descent']
    else:
        total_height = line_metrics[0]['height']
    # print(font_size, total_height, interline, scale, interline_ratio)
    # print([metric['height'] for metric in line_metrics])
    # print([metric['ascent'] for metric in line_metrics])
    # print([metric['descent'] for metric in line_metrics])
    # print(font_size, total_height, interline, scale)
    
    # Centrer verticalement le bloc de texte combiné dans la zone
    vertical_center = y0 + zone_height / 2
    horizontal_center = x0 + zone_width / 2
    
    for i, (metric, line) in enumerate(zip(line_metrics, text_lines)):
        text_width = metric['width']
        start_X = horizontal_center - text_width / 2
        start_Y = vertical_center - total_height / 2 + line_metrics[0]['ascent'] + i * interline
        svg_elements.extend(draw_text_line(line, start_X , start_Y, font, font_size, scale))
    
    return svg_elements

def flip(svg_elements, position):
    # Join the SVG elements into one string if they are in a list
    svg_elements = ''.join(svg_elements)
    # Wrap the elements with the group tag and transformations
    svg_elements = f'<g transform="scale(-1, 1) translate(-{position}, 0)">\n{svg_elements}</g>\n'
    return svg_elements

def generate_svg(svg_elements, output_file, loc_vis, loc_print = []):
    minX, minY, maxX, maxY = loc_vis # Dimensions de la zone de visualisation
    stroke_color = "black"  # Couleur du trait
    fill_color = "none"# "transparent"  # Couleur de remplissage
    stroke_width = 0.1  # Épaisseur du trait
    
    # Calculer la largeur et la hauteur pour viewBox
    width = maxX - minX
    height = maxY - minY
    
    # Utiliser les dimensions calculées pour viewBox
    viewBox = f"{minX} {minY} {width} {height}"
    if loc_print != []:
        printx, printy, printX, printY = loc_print
        rectangle = f"""<rect x="{printx}" y="{printy}" width="{printX}" height="{printY}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="{fill_color}" />"""
    
    with open(output_file, 'w') as f:
        # Écrire l'entête SVG avec les dimensions et la viewBox calculées
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="{viewBox}">\n')
        for path_data in svg_elements:
            f.write(f'{path_data}\n')
        if loc_print != []: f.write(f"{rectangle}")
        f.write('</svg>')
    print(f"SVG sauvegardé à {os.path.abspath(output_file)}")

def main():
    # Paramètres de texte
    text = "Un texte court"
    text = "Un long texte à diviser ou ajuster"
    font_path = '../static/fonts/Allison/Allison-Regular.ttf'
    font_size = 50
    
    # Paramètres visuels [mm]
    zoneWidth_mm = 100
    zoneHeight_mm = 40
    x_mm = 20
    y_mm = 10
    interline_ratio = 0.6
    
    # Générer le fichier SVG
    output_path = '../examples/outputs'
    loc_vis_mm = [0, 0, zoneWidth_mm, zoneHeight_mm]
    svg_text = text_svg(text, font_path, font_size, zoneWidth_mm - x_mm, zoneHeight_mm - y_mm, x_mm, y_mm, interline_ratio = interline_ratio)
    # Si pas de visualisation du cadre :
    generate_svg(svg_text, os.path.join(output_path, 'text_without.svg'), loc_vis_mm)
    # Si visualisation du cadre :
    loc_print_mm = [x_mm, y_mm, zoneWidth_mm - x_mm, zoneHeight_mm - y_mm]
    generate_svg(svg_text, os.path.join(output_path, 'text_with.svg'), loc_vis_mm, loc_print_mm)

if __name__ == "__main__":
    main()