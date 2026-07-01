import math

from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from svgtag.svg.base import SVG


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
    kerning_table = font["kern"].kernTables[0].kernTable if "kern" in font else {}
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
            if y_points:
                max_ascent = max(max_ascent, max(y_points))
                min_descent = min(min_descent, min(y_points))

    text_height = max_ascent - min_descent
    return text_height, max_ascent, min_descent


def calculate_interline(font, scale, interline_ratio):
    """
    Compute the specified spacing between two lines.
    """
    ascent = font["hhea"].ascent * scale
    descent = font["hhea"].descent * scale
    line_gap = font["hhea"].lineGap * scale
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
        "descent": min_descent * scale,
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
    kerning_table = font["kern"].kernTables[0].kernTable if "kern" in font else {}
    elements = []
    previous_glyph_name = None
    for char in text:
        glyph_name = font.getBestCmap()[ord(char)]
        if glyph_name in glyphset:
            glyph = glyphset[glyph_name]
            kerning = 0
            if previous_glyph_name:
                pair = (previous_glyph_name, glyph_name)
                kerning = (
                    kerning_table.get(pair, 0) * scale
                    if kerning_table and pair in kerning_table
                    else 0
                )
            x += kerning
            previous_glyph_name = glyph_name
            pen = SVGPathPen(glyphset)
            tpen = TransformPen(pen, (scale, 0, 0, -scale, x, y))
            glyph.draw(tpen)
            path_data = pen.getCommands()
            elements.append({"tag": "path", "attributes": {"d": path_data}})
            x += glyph.width * scale
    return elements



def split_text(text, n):
    """
    Split the text in several (n) lines, balancing line lengths.
    Respects manual line breaks (\n).
    
    Args:
        text: Text to split (may contain \n for manual breaks)
        n: Target number of lines
    
    Returns:
        List of text lines
    """
    # Check for manual line breaks first
    if '\n' in text:
        lines = [line.strip() for line in text.split('\n')]
        # Remove empty lines
        lines = [line for line in lines if line]
        return lines  # Return manual splits directly
    
    # Otherwise, auto-split
    words = text.split()
    
    if n == 1 or len(words) < n:
        return [text]
    
    # Distribute words to balance line LENGTH (characters)
    total_chars = sum(len(word) for word in words) + len(words) - 1  # +spaces
    target_chars_per_line = total_chars / n
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + (1 if current_line else 0)  # +1 for space
        
        # If adding this word exceeds target AND we have words, start new line
        if current_length + word_length > target_chars_per_line and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += word_length
    
    # Add last line
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines


def shape_text(text, font, zone_width, zone_height, scale, interline_ratio=0.8, n=None):
    """
    Determines text shape (number of lines, font size reduction).
    
    Args:
        text: Text to shape
        font: TTFont object
        zone_width, zone_height: Available space in mm
        scale: Initial scale factor
        interline_ratio: Line spacing ratio
        n: Optional forced number of lines (None = auto, integer = force N lines)
    
    Returns:
        (text_lines, n, new_scale): Split text, final line count, optimized scale
    """
    text_clean = text.replace('\n', ' ')

    line_metrics = calculate_line_metrics(text_clean, font, scale)
    interline = calculate_interline(font, scale, interline_ratio)
    
    # Track if n is forced
    n_forced = (n is not None)
    
    if n is None:
        # Auto-calculate number of lines
        if line_metrics["width"] > zone_width:
            n = max(2, math.ceil(line_metrics["width"] / zone_width * 0.5))
        else:
            n = 1
    # else: n is already the forced value
    
    # Split text
    if line_metrics["width"] > zone_width or n_forced:
        text_lines = split_text(text, n)
    else:
        text_lines = [text_clean]

    # Update n with actual line count (only if not forced)
    if not n_forced:
        n = len(text_lines)
    
    # Calculate dimensions
    line_metrics = [calculate_line_metrics(line, font, scale) for line in text_lines]
    total_height = (
        line_metrics[0]["ascent"] + (n - 1) * interline - line_metrics[-1]["descent"]
    )
    total_width = max([metric["width"] for metric in line_metrics])

    # Calculate optimal scale
    scale_by_width = zone_width / total_width
    scale_by_height = zone_height / total_height
    new_scale = scale * min(scale_by_width, scale_by_height)
    
    # Recalculate with new scale
    interline = calculate_interline(font, new_scale, interline_ratio)
    line_metrics = [calculate_line_metrics(line, font, new_scale) for line in text_lines]
    total_height = (
        line_metrics[0]["ascent"] + (n - 1) * interline - line_metrics[-1]["descent"]
    )
    total_width = max([metric["width"] for metric in line_metrics])
    
    # Verify fit (only if n not forced)
    if not n_forced:
        max_iterations = 5
        iteration = 0
        while (total_height > zone_height or total_width > zone_width) and iteration < max_iterations:
            if iteration == 0:
                print(f"WARNING: Text doesn't fit, increasing lines from {n}...")
            iteration += 1
            
            # Increase line count
            n += 1
            text_lines = split_text(text, n)
            
            # Recalculate everything
            line_metrics = [calculate_line_metrics(line, font, new_scale) for line in text_lines]
            interline = calculate_interline(font, new_scale, interline_ratio)
            total_height = (
                line_metrics[0]["ascent"] + (n - 1) * interline - line_metrics[-1]["descent"]
            )
            total_width = max([metric["width"] for metric in line_metrics])
            
            # Readjust scale if necessary
            if total_width > zone_width or total_height > zone_height:
                scale_by_width = zone_width / total_width
                scale_by_height = zone_height / total_height
                new_scale = new_scale * min(scale_by_width, scale_by_height)
                
                # Recalculate with new scale
                line_metrics = [calculate_line_metrics(line, font, new_scale) for line in text_lines]
                interline = calculate_interline(font, new_scale, interline_ratio)
                total_height = (
                    line_metrics[0]["ascent"] + (n - 1) * interline - line_metrics[-1]["descent"]
                )
                total_width = max([metric["width"] for metric in line_metrics])
    return text_lines, n, new_scale


def text_svg(
    text, font_path, font_size, zone_width, zone_height, x0, y0, interline_ratio=0.8, n=None,
    align="center",
):
    """
    Generate SVG for text fitted in a dedicated area.

    Args:
        text: Text to render
        font_path: Path to TTF font file
        font_size: Fixed font size in mm (None = auto-optimize)
        zone_width, zone_height: Available space in mm
        x0, y0: Top-left corner of text zone
        interline_ratio: Line spacing ratio (default 0.8)
        n: Optional forced number of lines (None = auto, integer = force N lines)
        align: Horizontal alignment within the zone — "center" (default),
            "left" or "right". Vertical alignment is always centred.

    Returns:
        SVG object with rendered text
    """
    if not isinstance(text, str):
        text = str(text)

    font = TTFont(font_path)
    unitsPerEm = font["head"].unitsPerEm

    # Initial scale
    if font_size is not None:
        scale = font_size / (72 * unitsPerEm) * 25.4
    else:
        scale = 100 / (72 * unitsPerEm) * 25.4

    svg = SVG("", ppi=96)

    text_lines, n, scale_max = shape_text(
        text, font, zone_width, zone_height, scale, interline_ratio, n
    )
    
    # Apply final scale
    if font_size is None:
        scale = scale_max
    else:
        scale = min(scale, scale_max)
    
    interline = calculate_interline(font, scale, interline_ratio)
    line_metrics = [calculate_line_metrics(line, font, scale) for line in text_lines]
    
    # Calculate total height
    if len(text_lines) > 1:
        total_height = (
            line_metrics[0]["ascent"] + (n - 1) * interline - line_metrics[-1]["descent"]
        )
    else:
        total_height = line_metrics[0]["height"]

    # Vertical alignment is always centred; horizontal follows `align`.
    vertical_center = y0 + zone_height / 2
    horizontal_center = x0 + zone_width / 2

    # Render all lines in a single group
    all_elements = []
    for i, (metric, line) in enumerate(zip(line_metrics, text_lines)):
        text_width = metric["width"]
        if align == "left":
            start_X = x0
        elif align == "right":
            start_X = x0 + zone_width - text_width
        else:
            start_X = horizontal_center - text_width / 2
        start_Y = (
            vertical_center - total_height / 2 + line_metrics[0]["ascent"] + i * interline
        )
        svg_elements = draw_text_line(line, start_X, start_Y, font, font_size, scale)
        all_elements.extend(svg_elements)

    # Add single group with all elements (important for mesh conversion)
    svg.add_group(all_elements, translate=[0, 0], scale=1.0)
    
    return svg


def flip(svg_elements, position):
    """
    Flip SVG elements horizontally around a position.
    
    Args:
        svg_elements: List of SVG element dictionaries
        position: X position to flip around
    
    Returns:
        List of flipped SVG elements
    """
    flipped_elements = []
    for element in svg_elements:
        if "scale" not in element:
            element["scale"] = 1

        # Horizontal flip
        element["scale"] = -1
        translate_x, translate_y = element.get("translate", [0, 0])
        element["translate"] = [position - translate_x, translate_y]

        flipped_elements.append(element)

    return flipped_elements

def get_text_dimensions(text, font_path, max_width, max_height, n=None):
    """
    Calculate actual dimensions of rendered text using font metrics.
    
    Args:
        text: Text to render
        font_path: Path to font file
        max_width: Maximum width available
        max_height: Maximum height available
        n: Line count override
    
    Returns:
        (width, height) of the actual text bounding box
    """
    from fontTools.ttLib import TTFont
    from ..svg.text import shape_text, calculate_interline, calculate_line_metrics
    
    # Load font
    font = TTFont(font_path)
    unitsPerEm = font["head"].unitsPerEm
    
    # Initial scale
    scale = 100 / (72 * unitsPerEm) * 25.4
    
    # Calculate text shape
    interline_ratio = 1.0
    text_lines, final_n, final_scale = shape_text(
        text, font, max_width, max_height, scale, interline_ratio, n
    )
    
    # Calculate final metrics
    interline = calculate_interline(font, final_scale, interline_ratio)
    line_metrics = [calculate_line_metrics(line, font, final_scale) for line in text_lines]
    
    # Total dimensions
    text_width = max([metric["width"] for metric in line_metrics])
    
    if len(text_lines) > 1:
        text_height = (
            line_metrics[0]["ascent"] + (final_n - 1) * interline - line_metrics[-1]["descent"]
        )
    else:
        text_height = line_metrics[0]["height"]

    return text_width, text_height


def add_thickened_text(target_svg, text_svg, offset, fill='black'):
    """Draw the *thickened* glyphs of ``text_svg`` into ``target_svg`` (2D).

    For laser / 3D-print legibility: thickens thin (esp. cursive) strokes by
    ``offset`` mm per side, without changing the font. The geometry lives in
    mesh.extrusion (glyph_polygons / thicken_polygons); this is the 2D drawing
    side. evenodd keeps the counters open.
    """
    from svgtag.mesh.extrusion import glyph_polygons, thicken_polygons
    for g in thicken_polygons(glyph_polygons(text_svg), offset):
        target_svg.add_path(g, fill=fill, fill_rule='evenodd')