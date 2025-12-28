"""
Exemple: Tag texte seul (sans forme)
Génère juste le texte positionné pour un circular tag
"""
from pathlib import Path
from svgtag.svg.base import SVG
from svgtag.svg.shapes import tag_circle_svg
from svgtag.svg.composition import add_text_zone, add_outline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tag" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")

# Obtenir le layout et le SVG de référence d'un circular tag
ref_svg, layout = tag_circle_svg(length=80, height=35, hole_diameter=6, border=3)

# Créer un SVG vide avec les mêmes caractéristiques
svg = SVG()
svg.width = ref_svg.width
svg.height = ref_svg.height
svg.viewBox = ref_svg.viewBox.copy()
svg.unit = ref_svg.unit

# Ajouter uniquement le texte
area = layout.get_area('main')
add_text_zone(svg, "Impression d'une étiquette", font_path, area)

svg.update_svg_content()
svg.generate_svg_file(str(output_path / "text_only.svg"))

add_outline(svg, area, color="blue")
svg.update_svg_content()
svg.generate_svg_file(str(output_path / "text_only_outline.svg"))

print(f"✓ Tag texte seul généré dans {output_path}")