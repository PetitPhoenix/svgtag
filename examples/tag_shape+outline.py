"""
Exemple: Tag avec forme et outlines de debug
Affiche les bordures de la zone de texte pour le debug
"""
from pathlib import Path
from svgtag.svg.shapes import tag_circle_svg, tag_rectangle_svg, tag_triangle_svg
from svgtag.svg.composition import add_outline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

# Rectangle basic (sans trou) avec outline
svg, layout = tag_rectangle_svg(length=80, height=35, hole_diameter=0, border=3)
area = layout.get_area('main')
add_outline(svg, area, color="blue")
svg.generate_svg_file(str(output_path / "basic_outline.svg"))

# Circle avec outline
svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)
area = layout.get_area('main')
add_outline(svg, area, color="red")
svg.generate_svg_file(str(output_path / "circle_outline.svg"))

# Rectangle avec outline
svg, layout = tag_rectangle_svg(length=80, height=35, hole_diameter=6, border=3)
area = layout.get_area('main')
add_outline(svg, area, color="red")
svg.generate_svg_file(str(output_path / "rectangle_outline.svg"))

# Triangle avec outline
svg, layout = tag_triangle_svg(length=80, height=35, hole_diameter=6, border=3)
area = layout.get_area('main')
add_outline(svg, area, color="red")
svg.generate_svg_file(str(output_path / "triangle_outline.svg"))

print(f"✓ Tags avec outlines générés dans {output_path}")