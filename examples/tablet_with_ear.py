"""
Exemple: Tablette - shape, avec texte, avec outline
"""
from pathlib import Path
from svgtag.svg.shapes import tablet_svg
from svgtag.svg.composition import add_text_zone, add_outline, add_border_outline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / "tablet" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

font_path = str(ROOT / "static" / "fonts" / "Impact" / "impact.ttf")
text="Ceci est un long texte qui raconte une histoire surprenante mais néanmoins inutile"
# =============================================================================
# 1. Shape seule (sans texte)
# =============================================================================
svg, layout = tablet_svg(
    width=80,
    height=129,
    padding=3,
    eyelet_outer_diameter=18,  # 8 + 2*5
    eyelet_hole_diameter=8,
    ear_offset=[5, 5]
)

svg.generate_svg_file(str(output_path / "tablet_shape.svg"))

# =============================================================================
# 2. Avec texte
# =============================================================================
svg, layout = tablet_svg(
    width=80,
    height=129,
    padding=3,
    eyelet_outer_diameter=18,
    eyelet_hole_diameter=8,
    ear_offset=[5, 5]
)

area = layout.get_area('main')
add_text_zone(svg, text, font_path, area)
svg.generate_svg_file(str(output_path / "tablet_with_text.svg"))

# =============================================================================
# 3. Avec texte et outline (debug)
# =============================================================================
svg, layout = tablet_svg(
    width=80,
    height=129,
    padding=3,
    eyelet_outer_diameter=18,
    eyelet_hole_diameter=8,
    ear_offset=[5, 5]
)

area = layout.get_area('main')
add_text_zone(svg, text, font_path, area)
add_outline(svg, area, color="red")
svg.generate_svg_file(str(output_path / "tablet_with_outline.svg"))

# =============================================================================
# 4. Avec texte et double outline - méthode 1 (debug)
# =============================================================================
svg, layout = tablet_svg(
    width=80,
    height=129,
    padding=8,  # ← Padding augmenté pour réduire la zone de texte
    eyelet_outer_diameter=18,
    eyelet_hole_diameter=8,
    ear_offset=[5, 5]
)

# Zone de texte (bleue - définie par padding=8)
area = layout.get_area('main')
add_outline(svg, area, color="blue", stroke_width=0.3)

# Zone imprimable étendue (rouge - déborde de 5mm)
add_border_outline(svg, area, border=5, color="red", stroke_width=0.3)

# Ajouter le texte
add_text_zone(svg, text, font_path, area)

svg.generate_svg_file(str(output_path / "tablet_double_outline1.svg"))

# =============================================================================
# 3. Avec texte et double outline - méthode 2 (debug)
# =============================================================================
svg, layout = tablet_svg(
    width=80,
    height=129,
    padding=3,
    eyelet_outer_diameter=18,
    eyelet_hole_diameter=8,
    ear_offset=[5, 5]
)

# Zone principale (rouge - définie par le layout)
area = layout.get_area('main')
add_outline(svg, area, color="red", stroke_width=0.3)

# Zone texte avec border interne supplémentaire (bleu)
text_border = 5  # 5mm de border interne supplémentaire
text_area = (
    area.x + text_border,
    area.y + text_border,
    area.width - 2 * text_border,
    area.height - 2 * text_border
)
add_outline(svg, text_area, color="blue", stroke_width=0.3)

# Ajouter le texte dans la zone bleue (plus petite)
add_text_zone(svg, text, font_path, text_area)

svg.generate_svg_file(str(output_path / "tablet_double_outline2.svg"))

print(f"✓ Tablettes générées dans {output_path}")