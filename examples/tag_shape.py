"""
Exemple: Tag avec forme uniquement (sans texte)
Génère un tag avec juste la forme circle et le trou
"""
from pathlib import Path
from svgtag.svg.shapes import tag_circle_svg, tag_rectangle_svg, tag_triangle_svg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

# Rectangle basic (sans trou)
svg, layout = tag_rectangle_svg(length=80, height=35, border=3)
svg.generate_svg_file(str(output_path / "basic.svg"))

# Circle
svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)
svg.generate_svg_file(str(output_path / "circle.svg"))

# Rectangle
svg, layout = tag_rectangle_svg(length=80, height=35, hole_diameter=6, border=3)
svg.generate_svg_file(str(output_path / "rectangle.svg"))

# Triangle
svg, layout = tag_triangle_svg(length=80, height=35, hole_diameter=6, border=3)
svg.generate_svg_file(str(output_path / "triangle.svg"))

print(f"✓ Tag forme seule généré dans {output_path}")