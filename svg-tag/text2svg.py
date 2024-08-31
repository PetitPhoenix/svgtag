from SVGprocess import SVG
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
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
    Define the SVG elements of a text
    
    Args:
        text: Text to draw.
        x, y: Initial position for the text.
        font_size: Font size.
        scale: Convertion from unitsPerEm in mm.
    
    Returns:
        List of dictionaries, each one representing a SVG element `<path>`.
    """
    glyphset = font.getGlyphSet()
    kerning_table = font['kern'].kernTables[0].kernTable if 'kern' in font else {}
    elements = []  # List to store the data elements of paths
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
            # Create a data element for each path
            elements.append({
                'tag': 'path',
                'attributes': {'d': path_data}
            })
            x += glyph.width * scale
    return elements

def split_text(text, n):
    """
    Split the text in several (n) lines.
    """
    words = text.split()
    # If the text shall be in one line of if the number of words is lower than the required number of lines
    if n == 1 or len(words) < n:
        return [text]
    
    # Computes approximatively the number of lines
    avg = len(words) // n
    lines = []
    start = 0
    for i in range(n - 1):  # Split in n-1 lines to make sure that all words are included
        end = start + avg
        lines.append(' '.join(words[start:end]))
        start = end
    
    # Add the rest of the words to the last line
    lines.append(' '.join(words[start:]))
    return lines

def shape_text(text, font, zone_width, zone_height, scale, interline_ratio = 0.8, n = []):
    """
    Defines the shape of the text (number of lines, reduces font size).
    """
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
    total_width = max([metric['width'] for metric in line_metrics]) # line_metrics[0]['width']
    
    if total_width / total_height < aspect_ratio:
        scale *= zone_height / total_height
    else:
        scale *= zone_width / total_width
        
    return text_lines, n, scale

def text_svg(text, font_path, font_size, zone_width, zone_height, x0, y0, interline_ratio = 0.8, n = []):
    """
    General procedure that tries to fit the text in a dedicated area.
    """
    if not isinstance(text, str):
        text = str(text)
    
    font = TTFont(font_path)
    unitsPerEm = font['head'].unitsPerEm
    if font_size is not None:
        scale = font_size / (72 * unitsPerEm) * 25.4
    else:
        scale = 100 / (72 * unitsPerEm) * 25.4
    
    svg = SVG('', ppi=96)
    text_lines, n, scale_max = shape_text(text, font, zone_width, zone_height, scale, interline_ratio)
    if font_size is None:
        scale = scale_max
    interline = calculate_interline(font, scale, interline_ratio)
    
    line_metrics = [calculate_line_metrics(line, font, scale) for line in text_lines]
    if len(text_lines) > 1:
        total_height = line_metrics[0]['ascent'] + (n - 1) * interline - line_metrics[-1]['descent']
    else:
        total_height = line_metrics[0]['height']
    
    # Center vertically the combined text bloc within the area
    vertical_center = y0 + zone_height / 2
    horizontal_center = x0 + zone_width / 2
    
    for i, (metric, line) in enumerate(zip(line_metrics, text_lines)):
        text_width = metric['width']
        start_X = horizontal_center - text_width / 2
        start_Y = vertical_center - total_height / 2 + line_metrics[0]['ascent'] + i * interline
        svg_elements = draw_text_line(line, start_X , start_Y, font, font_size, scale)
        svg.add_group(svg_elements, translate=[0, 0], scale=1.0)
    return svg

def flip(svg_elements, position):
    flipped_elements = []
    for element in svg_elements:
        # If the element has transformations, apply a flip
        if 'transform' not in element:
            element['transform'] = {'translate': [0, 0], 'scale': 1.0}

        # Add a horizontal scaling transformation (flip)
        element['transform']['scale'] = -1  # Invert horizontally
        translate_x, translate_y = element['transform'].get('translate', [0, 0])
        # Adjust the translation to compensation the inversion
        element['transform']['translate'] = [position - translate_x, translate_y]
        
        flipped_elements.append(element)
    
    return flipped_elements


def main():
    # Text parameters
    text = "Un long texte à diviser ou ajuster"
    font_path = '../static/fonts/Allison/Allison-Regular.ttf'
    font_size = None
    
    # Visual parameters [mm]
    zoneWidth_mm = 80
    zoneHeight_mm = 40
    x_mm = 20
    y_mm = 10
    interline_ratio = 0.6
    
    # Generate SVG file
    output_path = '../examples/outputs'
    svg_text = text_svg(text, font_path, font_size, zoneWidth_mm - x_mm, zoneHeight_mm - y_mm, x_mm, y_mm, interline_ratio = interline_ratio)
    svg_text.unit = 'mm'
    svg_text.width = zoneWidth_mm
    svg_text.height = zoneHeight_mm
    svg_text.viewBox = [0, 0, zoneWidth_mm, zoneHeight_mm]
    svg_text.update_svg_content()
    svg_text.add_element("rect", {"x": x_mm, "y": y_mm, "width": zoneWidth_mm - x_mm, "height": zoneHeight_mm - y_mm, "stroke": "black", "fill": "transparent", "stroke-width": 0.1 }, {"translate": (0, 0), "scale": 1})
    svg_text.generate_svg_file(os.path.join(output_path, 'text_rec.svg'))

if __name__ == "__main__":
    main()
    