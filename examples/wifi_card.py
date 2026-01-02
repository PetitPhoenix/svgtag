"""
Example: WiFi QR code card generation
Generates a card with QR code and network information
"""
from pathlib import Path
from svgtag.svg.shapes.wifi import wifi_card_svg
from svgtag.svg.composition import add_text_zone
from svgtag.svg.text import text_svg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)

static_files_path = str(ROOT / "static")
signal_icon_path = str(ROOT / "static" / "images" / "network.svg")

# Font paths
fonts = {
    'title': str(ROOT / "static" / "fonts" / "Southmore" / "Southmore.ttf"),
    'subtitle': str(ROOT / "static" / "fonts" / "BillionDreams" / "BillionDreams.ttf"),
    'label': str(ROOT / "static" / "fonts" / "Stark" / "Stark.ttf"),
    'value': str(ROOT / "static" / "fonts" / "Kollektif" / "Kollektif.ttf"),
}

# Text configuration
texts = {
    'title': {'text': 'Bienvenue', 'font_size': 36},
    'subtitle': {'text': 'Profitez du wifi', 'font_size': 20},
    'network_label': {'text': 'Réseau', 'font_size': 20},
    'password_label': {'text': 'Mot de passe', 'font_size': 20},
}

# WiFi parameters
network = "MyNetwork"
password = "MyPassword"
protocol = "WPA"
hidden = False

print(f"Generating WiFi card...")
print(f"  Network: {network}")
print(f"  Password: {password}")

# 1. Generate base card with QR code
svg, layout = wifi_card_svg(
    network=network,
    password=password,
    width_mm=100,
    height_mm=100,
    padding_mm=5,
    protocol=protocol,
    hidden=hidden,
    signal_icon_path=signal_icon_path
)

# 2. Add title
title_area = layout.get_area('title')
title_svg = text_svg(
    text=texts['title']['text'],
    font_path=fonts['title'],
    font_size=texts['title']['font_size'],
    zone_width=title_area.width,
    zone_height=title_area.height,
    x0=title_area.x,
    y0=title_area.y
)
svg.add_group(title_svg.elements)

# 3. Add subtitle
subtitle_area = layout.get_area('subtitle')
subtitle_svg = text_svg(
    text=texts['subtitle']['text'],
    font_path=fonts['subtitle'],
    font_size=texts['subtitle']['font_size'],
    zone_width=subtitle_area.width,
    zone_height=subtitle_area.height,
    x0=subtitle_area.x,
    y0=subtitle_area.y
)
svg.add_group(subtitle_svg.elements)

# 4. Add network label
network_label_area = layout.get_area('network_label')
network_label_svg = text_svg(
    text=texts['network_label']['text'],
    font_path=fonts['label'],
    font_size=texts['network_label']['font_size'],
    zone_width=network_label_area.width,
    zone_height=network_label_area.height,
    x0=network_label_area.x,
    y0=network_label_area.y
)
svg.add_group(network_label_svg.elements)

# 5. Add network value
network_value_area = layout.get_area('network_value')
network_value_svg = text_svg(
    text=network,
    font_path=fonts['value'],
    font_size=14,
    zone_width=network_value_area.width,
    zone_height=network_value_area.height,
    x0=network_value_area.x,
    y0=network_value_area.y
)
svg.add_group(network_value_svg.elements)

# 6. Add password label
password_label_area = layout.get_area('password_label')
password_label_svg = text_svg(
    text=texts['password_label']['text'],
    font_path=fonts['label'],
    font_size=texts['password_label']['font_size'],
    zone_width=password_label_area.width,
    zone_height=password_label_area.height,
    x0=password_label_area.x,
    y0=password_label_area.y
)
svg.add_group(password_label_svg.elements)

# 7. Add password value
password_value_area = layout.get_area('password_value')
password_value_svg = text_svg(
    text=password,
    font_path=fonts['value'],
    font_size=14,
    zone_width=password_value_area.width,
    zone_height=password_value_area.height,
    x0=password_value_area.x,
    y0=password_value_area.y
)
svg.add_group(password_value_svg.elements)

# 8. Save
filename = "wifi_card.svg"
svg.generate_svg_file(str(output_path / filename))

print(f"\n✓ WiFi card generated: {output_path / filename}")