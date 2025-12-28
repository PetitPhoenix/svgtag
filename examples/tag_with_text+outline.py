"""
Exemple: Tags complets avec texte
Tags classiques avec formes et texte
"""
from pathlib import Path
from svgtag.svg.shapes import tag_circle_svg, tag_rectangle_svg, tag_triangle_svg
from svgtag.svg.composition import add_text_zone, add_outline, add_border_outline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")

border = 3

# Tag basique sans trou
svg, layout = tag_rectangle_svg(length=80, height=35, border=border, corner_radius=3)
area = layout.get_area('main')
add_text_zone(svg, "Impression d'une étiquette", font_path, area, outline=True)
add_outline(svg, area, color="red")
add_border_outline(svg, area, border=border, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "tag_basic_outline.svg"))

# Tag Circle avec texte
svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=border)
area = layout.get_area('main')
add_text_zone(svg, "Impression d'une étiquette", font_path, area, outline=True)
add_outline(svg, area, color="red")
add_border_outline(svg, area, border=border, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "tag_circle_outline.svg"))

# Tag Rectangle avec texte
svg, layout = tag_rectangle_svg(length=80, height=35, hole_diameter=6, border=border, corner_radius=3)
area = layout.get_area('main')
add_text_zone(svg, "Impression d'une étiquette", font_path, area, outline=True)
add_outline(svg, area, color="red")
add_border_outline(svg, area, border=border, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "tag_rectangle_outline.svg"))

# Tag Triangle avec texte
svg, layout = tag_triangle_svg(length=80, height=35, hole_diameter=6, border=border)
area = layout.get_area('main')
add_text_zone(svg, "Impression d'une étiquette", font_path, area, outline=True)
add_outline(svg, area, color="red")
add_border_outline(svg, area, border=border, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "tag_triangle_outline.svg"))

print(f"✓ Tags avec texte générés dans {output_path}")