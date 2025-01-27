import os
import datetime
from SVGtag.generators.wifi import QR_gen
from SVGtag.scripts.export import prepare_target_directory, convert_svg_with_inkscape, zip_subdirectory

# Paramètres personnels
inkscape_path = r"C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin\Inkscape.exe"

# Paramètres de réseau
network = 'MyNetwork'
password = 'MyPassword'
protocol = 'WPA/WPA2'
hidden = 'true'

# Paramètres de la forme
width_mm = 100
height_mm = 100
padding_mm = 5

# Éléments de texte
text_elements = [
    {'text': 'Bienvenue', 'width': 2/3, 'height': 1/4, 'x': 0, 'y': 0, 'font': 'Southmore.ttf', 'fontsize': 30},
    {'text': 'Profitez du wifi', 'width': 2/3, 'height': 1/10, 'x': 0, 'y': 1/4, 'font': 'BillionDreams.ttf', 'fontsize': 20},
    {'text': 'Réseau', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 6/12, 'font': 'Stark.ttf', 'fontsize': 18},
    {'text': network, 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 7.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13},
    {'text': 'Mot de passe', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 9/12, 'font': 'Stark.ttf', 'fontsize': 18},
    {'text': password, 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 10.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13}
]

# Paramètres de fichier
now = datetime.datetime.now()
formatted_date = now.strftime("%Y%m%d-%H%M")
client_ref = 'Client ABC'
order_ref = 'XYZ'
filename = f"{client_ref}_{order_ref}_{formatted_date}"
output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'wifi')
os.makedirs(output_path, exist_ok=True)

# Générer le code QR
svg_instance = QR_gen(network, password, protocol, hidden, text_elements, width_mm, height_mm, padding_mm)

# Enregistrer le fichier SVG
output_file = os.path.join(output_path, filename + '.svg')
svg_instance.generate_svg_file(output_file)

print(f"QR code SVG generated at: {output_file}")


# Création d'un ensemble de fichiers avec Inkscape
output_formats = ['png', 'jpg', 'pdf', 'eps', 'dxf']
dpi = 600
svg_file_path = prepare_target_directory(output_file)
convert_svg_with_inkscape(svg_file_path, inkscape_path, output_formats, dpi)
directory = os.path.dirname(svg_file_path)
zip_subdirectory(directory)