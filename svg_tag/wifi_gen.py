import io
import os
from text2svg import text_svg
from SVGprocess import SVG, read_svg
import qrcode
# https://github.com/lincolnloop/python-qrcode

def QR_svg(network, password, protocol, hidden, box_size=10, border=0):
    # factory = qrcode.image.svg.SvgImage # Simple factory, just a set of rects
    # factory = qrcode.image.svg.SvgFragmentImage # Fragment factory (also just a set of rects)
    factory = qrcode.image.svg.SvgPathImage # Combined path factory, fixes white space that may occur when zooming   # Utilisez SvgPathImage pour un SVG compact
    #SvgSquareDrawer, SvgCircleDrawer, SvgPathSquareDrawer, or SvgPathCircleDrawer
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
        image_factory=factory,
    )
    
    qr.add_data(f'WIFI:T:{protocol};S:{network};P:{password};H:{hidden};;')
    qr.make(fit=True)
    img = qr.make_image()
    
    svg_io = io.BytesIO()
    img.save(svg_io)
    svg_string = svg_io.getvalue().decode('utf-8')
    
    # qr = qrcode.make(f'WIFI:T:{protocol};S:{network};P:{password};H:{hidden};;', 
    #                      image_factory=factory, 
    #                      box_size=box_size,
    #                      border=border)
    return svg_string


# ------------------------------------------------
# Paramètres de réseau
network='Mon réseau'
password='Mon mot de passe'
protocol='WPA/WPA2'
hidden='true'

# Paramètres de la forme
width_mm = 100
height_mm = 100
padding_mm = 5
thk = 1
x_mm = 0
y_mm = 0

text_elements = [
    {'text': 'Bienvenue', 'width': 2/3, 'height': 1/4, 'x': 0, 'y': 0, 'font': 'Southmore.ttf', 'fontsize': 30},
    {'text': 'Profitez du wifi', 'width': 2/3, 'height': 1/10, 'x': 0, 'y': 1/4, 'font': 'BillionDreams.ttf', 'fontsize': 20},
    {'text': 'Réseau', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 6/12, 'font': 'Stark.ttf', 'fontsize': 18},
    {'text': f'{network}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 7.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13},
    {'text': 'Mot de passe', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 9/12, 'font': 'Stark.ttf', 'fontsize': 18},
    {'text': f'{password}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 10.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13}
]

for element in text_elements:
    element['width'] = element['width']*(width_mm - 2 * padding_mm)
    element['height'] = element['height']*(height_mm - 2 * padding_mm)
    element['x'] = padding_mm
    element['y'] = element['y']*(height_mm - 2 * padding_mm) + padding_mm


svg_instance = SVG()
svg_instance.unit = 'mm'
svg_instance.width = width_mm
svg_instance.height = height_mm
svg_instance.viewBox = [0, 0, width_mm, height_mm]

for element in text_elements:
    font_path = f'./static/fonts/{element["font"]}'
    svg_data = text_svg(
        text=element['text'],
        font_path=font_path,
        font_size=element['fontsize'],
        zone_width=element['width'],
        zone_height=element['height'],
        x0=element['x'],
        y0=element['y']
    )
    svg_instance.add_group(svg_data.elements, translate=[0, 0], scale=1.0)
    # svg_instance.add_element("rect", {"x": element['x'], 
    #                               "y": element['y'], 
    #                               "width": element['width'],
    #                               "height": element['height'],
    #                               "stroke": "black", "fill": "none", "stroke-width": 0.1 }, 
    #                      {"translate": (0, 0), "scale": 1})

qr_svg = QR_svg(network, password, protocol, hidden, box_size=10, border=0)
qr_svg = SVG(qr_svg)
svg_instance.add_group(qr_svg.elements, 
                       translate=[width_mm / 2 + padding_mm, height_mm / 2 + padding_mm], 
                       scale=min((width_mm / 2 - 2 * padding_mm) / qr_svg.width, (height_mm / 2 - 2 * padding_mm) / qr_svg.height))

wifi = read_svg(r'.\static\images\wifi.svg')
wifi = SVG(wifi)
scale = (width_mm / 6) / wifi.width
svg_instance.add_group(wifi.elements, 
                       translate=[width_mm * 3 / 4 - wifi.width * scale / 2, height_mm / 2 - wifi.height * scale / 2], 
                       scale=scale)

signal = read_svg(r'.\static\images\network.svg')
signal = SVG(signal)
scale = min((width_mm / 3 - 2 * padding_mm) / signal.width, (height_mm / 2 - 2 * padding_mm) / signal.height)
svg_instance.add_group(signal.elements, 
                       translate=[width_mm * 2 / 3, height_mm / 4 - signal.height * scale / 2], 
                       scale=scale)

filename = 'test'
folder = r'.\outputs'
svg_instance.generate_svg_file(os.path.join(folder, filename + '.svg'))

import subprocess

def convert_svg_to_png(inkscape_path, svg_file, png_file):
    command = [
        inkscape_path,
        svg_file,  # Chemin du fichier SVG d'entrée
        '--export-type=png',
        '--export-filename=' + png_file,  # Chemin du fichier PNG de sortie
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Conversion réussie : '{svg_file}' vers '{png_file}'")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la conversion : {e}")

# Exemple d'utilisation
inkscape_path = "C:\\TOOLS\\01_Portable\\InkscapePortable\\App\\Inkscape\\bin\\inkscape.exe"

convert_svg_to_png(inkscape_path, os.path.join(folder, filename + '.svg'), os.path.join(folder, filename + '.png'))

# import cairosvg

# def convert_svg_to_png(svg_input, png_output):
#     """
#     Convertit un fichier SVG en fichier PNG.

#     Args:
#     svg_input (str): Le chemin vers le fichier SVG source.
#     png_output (str): Le chemin où le fichier PNG résultant sera sauvegardé.
#     """
#     cairosvg.svg2png(url=svg_input, write_to=png_output)

# #set PATH=%PATH%;C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin\
# # echo %PATH%

# convert_svg_to_png(os.path.join(folder, filename + '.svg'), os.path.join(folder, filename + '.png'))
