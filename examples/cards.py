import sys
import os
import datetime

parent_dir = os.path.dirname(os.getcwd())
svg_tag_path = os.path.join(parent_dir, 'svg_tag')
sys.path.append(svg_tag_path)

import export
from SVGprocess import SVG, read_svg
from text2svg import text_svg

def card_gen(text_elements, width_mm, height_mm, padding_mm, phi=None):
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
        font_path = f'../static/fonts/{element["font"].replace(".ttf", "")}/{element["font"]}'
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
    
    svg_instance.add_rectangle(x=0, y=0, width=width_mm, height=height_mm, stroke="black", fill="none", radius=5, stroke_width=0.1)

    if phi != None:
        svg_instance.add_element("circle", {"cx": f"{width_mm - phi - padding_mm}", "cy": f"{height_mm / 2}", "r": f"{phi / 2}", "stroke": "black", "fill": "none", "stroke-width": "0.1"}, {"translate": (0, 0), "scale": 1})
    return svg_instance

def generate_participant_cards(name, title, discipline, location, base_folder, filename, output_formats = ['png', 'jpg', 'pdf', 'eps', 'dxf'], prep_zip = False):
    # Paramètres de la forme
    width_mm = 85
    height_mm = 54
    padding_mm = 5
    phi = 5
    
    text_elements = [
        {'text': f'{name}',       'width': 1,   'height': 1/5, 'x': 0, 'y': 0,   'font': 'Kollektif.ttf', 'fontsize': 22},
        {'text': f'{title}',      'width': 1,   'height': 1/5, 'x': 0, 'y': 1/4, 'font': 'Kollektif.ttf', 'fontsize': 20}, 
        {'text': f'{discipline}', 'width': 1/2, 'height': 1/5, 'x': 0, 'y': 3/5, 'font': 'Allison.ttf', 'fontsize': 22}, 
        {'text': f'{location}',   'width': 1/2, 'height': 1/5, 'x': 0, 'y': 4/5, 'font': 'Allison.ttf', 'fontsize': 22}
    ]
    
    # Generate a svg
    svg_instance = card_gen(text_elements, width_mm, height_mm, padding_mm, phi)
    svg_file_path = os.path.join(base_folder, filename + '.svg')
    svg_instance.generate_svg_file(svg_file_path)
    
    # Outputs in different formats
    if output_formats != None:
        inkscape_path = r"C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin\Inkscape.exe"
        dpi = 600
        svg_file_path = export.prepare_target_directory(svg_file_path)
        export.convert_svg_with_inkscape(svg_file_path, inkscape_path, output_formats, dpi)
        
    # Create a zip
    if prep_zip == True or output_formats is not None:
        directory = os.path.dirname(svg_file_path)
        export.zip_subdirectory(directory)

if __name__ == "__main__":
    # Paramètres de fichier
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y%m%d-%H%M")
    client_ref = 'Client ABC'
    order_ref = 'XYZ'
    
    client_ref = 'EDF RE'
    order_ref = '2024-001'
    
    filename = f"{client_ref}_{order_ref}_{formatted_date}"
    folder = r'..\examples\outputs\cards'
    
    # # Single card generation
    # name = 'My name'
    # title = 'Doing good stuff here'
    # company = 'I work here'
    # location = 'Paris - France'
    # generate_participant_cards(name, title, company, location, folder)
    
    # Several card generation
    import pandas as pd
    file_path = r'C:\Users\sbesnard\EDF Renouvelables\Offshore 2024 Seminar - Orga team - Orga team\Attendees.csv'
    data = pd.read_csv(file_path, sep=';')
    data = data[data['Participation'].str.lower() == 'yes']
    
    # base_folder = os.path.join(folder, f"{client_ref}_{order_ref}_{formatted_date}")
    base_folder = os.path.join(folder, f"{client_ref}_{order_ref}")
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    for index, row in data.iterrows():
        name = row['Name']
        title = row['Position']
        discipline = row['DPT']
        location = row['Location']
        generate_participant_cards(name, title, discipline, location, base_folder, filename = name, 
                                   output_formats = ['png', 'pdf'], prep_zip = True) #output_formats = ['png', 'pdf'] or None