"""
Example: generic QR code card generation (2D SVG).

Same idea as `wifi_card.py`, but built on the payload-agnostic `qr_card_svg`:
the QR encodes an arbitrary string (here a URL). Swap `payload` for any other
string (mailto:, tel:, SMSTO:, BEGIN:VCARD..., geo:, raw text, or the WiFi
`WIFI:...` format) to make a different card.
"""
from pathlib import Path
from svgtag.svg.shapes.qr import qr_card_svg
from svgtag.geom.shapes import rounded_rectangle
from svgtag.svg.text import text_svg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

# Font paths
fonts = {
    'title': str(ROOT / "static" / "fonts" / "Southmore" / "Southmore.ttf"),
    'label': str(ROOT / "static" / "fonts" / "Stark" / "Stark.ttf"),
    'value': str(ROOT / "static" / "fonts" / "Kollektif" / "Kollektif.ttf"),
}

# --- Payload : n'importe quelle chaîne. Ici une URL. -----------------------
url = "https://github.com/PetitPhoenix/svgtag"
payload = url

# Text engraved on the card (left of the QR)
texts = {
    'title':         {'text': 'Scannez-moi', 'font': 'title', 'font_size': 36, 'zone': 'title'},
    'network_label': {'text': 'Lien',        'font': 'label', 'font_size': 20, 'zone': 'network_label'},
    'network_value': {'text': url, 'font': 'value', 'font_size': 14, 'zone': 'network_value'},
}

width = 120
height = 120

print("Generating QR card (2D)...")
print(f"  Payload: {payload}")

# 1. Base card with QR code
svg, layout = qr_card_svg(
    payload,
    width_mm=width,
    height_mm=height,
    padding_mm=5,
    icon_path=None,   # mets une icône SVG ici pour la graver en haut à droite
)

# 1.5 Card outline
outline = rounded_rectangle(width=width, height=height, corner_radius=5, x=0, y=0)
svg.add_path(outline, stroke='black', stroke_width='0.1', fill='none')

# 2. Engrave the text in its layout zones
for cfg in texts.values():
    area = layout.get_area(cfg['zone'])
    if area is None:
        continue
    t = text_svg(
        text=cfg['text'], font_path=fonts[cfg['font']], font_size=cfg['font_size'],
        zone_width=area.width, zone_height=area.height, x0=area.x, y0=area.y,
    )
    svg.add_group(t.elements)

# 3. Save
filename = "qr_card.svg"
svg.generate_svg_file(str(output_path / filename))
print(f"\n✓ QR card generated: {output_path / filename}")
