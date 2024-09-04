import sys
import os
import datetime

parent_dir = os.path.dirname(os.getcwd())
svg_tag_path = os.path.join(parent_dir, 'svg_tag')
sys.path.append(svg_tag_path)

import wifi_gen
import export

# Paramètres de réseau
network='Mon réseau'
password='Mon mot de passe'
protocol='WPA/WPA2'
hidden='true'

# Paramètres de la forme
width_mm = 120
height_mm = 100
padding_mm = 5
thk = 1
x_mm = 0
y_mm = 0

# Paramètres de fichier
now = datetime.datetime.now()
formatted_date = now.strftime("%Y%m%d-%H%M")
client_ref = 'Client ABC'
order_ref = 'XYZ'
filename = f"{client_ref}_{order_ref}_{formatted_date}"
folder = r'..\examples\outputs\wifi'


text_elements = [
    {'text': 'Bienvenue', 'width': 2/3, 'height': 1/4, 'x': 0, 'y': 0, 'font': 'Southmore.ttf', 'fontsize': 30},
    {'text': 'Profitez du wifi', 'width': 2/3, 'height': 1/10, 'x': 0, 'y': 1/4, 'font': 'BillionDreams.ttf', 'fontsize': 20},
    {'text': 'Réseau', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 6/12, 'font': 'Stark.ttf', 'fontsize': 18},
    {'text': f'{network}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 7.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13},
    {'text': 'Mot de passe', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 9/12, 'font': 'Stark.ttf', 'fontsize': 18},
    {'text': f'{password}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 10.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13}
]

svg_instance = wifi_gen.QR_gen(network, password, protocol, hidden, text_elements, width_mm, height_mm, padding_mm)

svg_file_path = os.path.join(folder, filename + '.svg')
svg_instance.generate_svg_file(svg_file_path)

inkscape_path = r"C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin\Inkscape.exe"
output_formats = ['png', 'jpg', 'pdf', 'eps', 'dxf']
dpi = 600
svg_file_path = export.prepare_target_directory(svg_file_path)
export.convert_svg_with_inkscape(svg_file_path, inkscape_path, output_formats, dpi)

directory = os.path.dirname(svg_file_path)
# export.zip_subdirectory(directory)