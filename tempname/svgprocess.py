import os
import re

def read_svg(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_svg(svg_content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(svg_content)

class SVG:
    def __init__(self, content="", ppi=96):
        self.content = content
        self.ppi = ppi
        self.elements = []
        self.header = '<svg xmlns="http://www.w3.org/2000/svg">'
        self.unit = 'px'
        self.width, self.height = None, None
        self.viewBox = self.x = self.y = None
        # Analyser le contenu initial s'il est fourni
        if self.content:
            self.parse_svg()
    
    def parse_svg(self):
        self.extract_header()
        self.extract_dimensions()
        self.extract_elements_and_transforms(self.content)
    
    def parse_element_attributes(self, attrs_string):
        # Simplification: parse l'attribut 'd' pour <path>, devra être étendu pour d'autres attributs/éléments
        attributes = {}
        d_match = re.search(r'd="([^"]*)"', attrs_string)
        if d_match:
            attributes['d'] = d_match.group(1)
        # Ajoutez ici l'extraction d'autres attributs selon les besoins
        return attributes
    
    def extract_header(self):
        match = re.search(r'<svg[^>]*>\n', self.content)
        if match:
            self.header = match.group(0)
            
    def extract_dimensions(self):
        width_match = re.search(r'width="([\d.]+)(px|mm|cm)?', self.content)
        height_match = re.search(r'height="([\d.]+)(px|mm|cm)?', self.content)
        viewBox_match = re.search(r'viewBox="([\d.\s]+)"', self.content)
        
        if width_match:
            self.width = float(width_match.group(1))
            if width_match.group(2):
                self.unit = width_match.group(2)
        
        if height_match:
            self.height = float(height_match.group(1))
        
        if viewBox_match:
            self.viewBox = list(map(float, viewBox_match.group(1).split()))
            if len(self.viewBox) == 4:
                self.x, self.y, viewBoxWidth, viewBoxHeight = self.viewBox
                if not width_match:
                    self.width = viewBoxWidth
                if not height_match:
                    self.height = viewBoxHeight
                self.cx, self.cy = self.x + self.width / 2, self.y + self.height / 2
    
    def extract_elements_and_transforms(self, content, parent_translate=[0.0, 0.0], parent_scale=1.0):
        # Gérer les groupes récursivement
        group_matches = re.findall(r'<g([^>]*)>(.*?)</g>', content, re.DOTALL)
        for group_match in group_matches:
            group_attrs = group_match[0]
            group_content = group_match[1]
            group_transform = self.extract_transform_details(group_attrs)
            # Combinez les transformations du groupe avec celles du parent
            combined_translate = [parent_translate[0] + group_transform[0][0], parent_translate[1] + group_transform[0][1]]
            combined_scale = parent_scale * group_transform[1]
            self.extract_elements_and_transforms(group_content, combined_translate, combined_scale)
        
        # Ne pas ajouter les éléments ici
        # Extraire les <path> et autres éléments souhaités en répétant le schéma ci-dessous
        
        if not group_matches: self.extract_and_add_elements('path', content, parent_translate, parent_scale)
        # Ajoutez d'autres appels à extract_and_add_elements pour d'autres balises SVG ici
    
    def extract_and_add_elements(self, tag, content, parent_translate, parent_scale):
        element_matches = re.findall(f'<{tag}([^>]*)/>', content)
        for element_attrs in element_matches:
            attributes = self.parse_element_attributes(element_attrs)
            element_transform = self.extract_transform_details(element_attrs)
            final_translate = [parent_translate[0] + element_transform[0][0], parent_translate[1] + element_transform[0][1]]
            final_scale = parent_scale * element_transform[1]
            
            # Ajout de validation avant d'ajouter l'élément
            if isinstance(attributes, dict): 
                self.elements.append({
                    'tag': tag,
                    'attributes': attributes,
                    'transform': {'translate': final_translate, 'scale': final_scale}
                })
            else:
                print(f"Warning: Attributes for element <{tag}/> are not a dictionary. Skipping element.")
    
    def extract_transform_details(self, transform_string):
        translate_match = re.search(r'translate\(([^)]*)\)', transform_string)
        scale_match = re.search(r'scale\(([^)]*)\)', transform_string)
        
        translate = [float(n) for n in translate_match.group(1).split(',')] if translate_match else [0.0, 0.0]
        scale = float(scale_match.group(1)) if scale_match else 1.0
        
        return translate, scale
    
    def add_svg(self, other_svg):
        """Ajoute les éléments d'un autre objet SVG à celui-ci."""
        for element in other_svg.elements:
            self.elements.append(element)
    
    def add_element(self, tag, attributes, transform=None):
        """Ajoute un élément SVG à la liste des éléments."""
        if isinstance(attributes, dict):
            element = {"tag": tag, "attributes": attributes, "transform": transform}
            self.elements.append(element)
        else:
            print(f"Warning: Attributes for element <{tag}/> are not a dictionary. Skipping element.")

    
    def add_path(self, d, translate=[0, 0], scale=1.0):
        """Ajoute un chemin à la liste des éléments avec transformation optionnelle."""
        element = {
            'tag': 'path',
            'attributes': {'d': d},
            'transform': {'translate': translate, 'scale': scale}
        }
        self.elements.append(element)
        
    def add_group(self, elements, translate=[0, 0], scale=1.0):
        """Ajoute un groupe d'éléments à la liste des éléments avec transformation optionnelle."""
        group = {
            'tag': 'g',
            'elements': elements,
            'transform': {'translate': translate, 'scale': scale}
        }
        self.elements.append(group)
    
    def add_rectangle(self, x, y, width, height, stroke="black", fill="none", radius="0", stroke_width=0.1):
        """Ajoute un rectangle à la liste des éléments."""
        attributes = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'stroke': stroke,
            'fill': fill,
            'rx': radius,
            'stroke-width': stroke_width
        }
        element = {
            'tag': 'rect',
            'attributes': attributes
        }
        self.elements.append(element)
    
    def convert_units(self, target_unit):
        if target_unit == self.unit:
            return  # No conversion needed
        
        # Determine the conversion function based on the target unit
        if target_unit == 'mm' and self.unit == 'px':
            conversion_func = self.px_to_mm
            scale_conversion = 25.4 / self.ppi
        elif target_unit == 'px' and self.unit == 'mm':
            conversion_func = self.mm_to_px
            scale_conversion = self.ppi / 25.4
        else:
            return  # Invalid unit conversion
        
        # Convert dimensions
        self.width = conversion_func(self.width) if self.width is not None else None
        self.height = conversion_func(self.height) if self.height is not None else None
        self.viewBox = [conversion_func(value) for value in self.viewBox] if self.viewBox else []
        self.x = conversion_func(self.x) if self.x is not None else None
        self.y = conversion_func(self.y) if self.y is not None else None
        self.cx = conversion_func(self.cx) if self.cx is not None else None
        self.cy = conversion_func(self.cy) if self.cy is not None else None
        
        # Adjust scale and translate for each path
        for element in self.elements:
            element['transform']['scale'] *= scale_conversion
            element['transform']['translate'] = [conversion_func(t) for t in element['transform']['translate']]
        
        self.unit = target_unit
        self.update_svg_content()
    
    def format_attributes(self, attributes):
        """Formatte les attributs d'un élément SVG en chaîne pour l'inclusion dans le balisage."""
        return ' '.join(f'{key}="{value}"' for key, value in attributes.items())

    def process_element(self, element):
        """Traite un seul élément SVG pour générer sa représentation en chaîne."""
        if isinstance(element, dict):
            attributes_str = self.format_attributes(element.get('attributes', {}))
            if element.get('transform'):
                transform_parts = []
                if 'translate' in element['transform']:
                    translate = element['transform']['translate']
                    transform_parts.append(f'translate({translate[0]}, {translate[1]})')
                if 'scale' in element['transform']:
                    scale = element['transform']['scale']
                    if scale != 1:
                        transform_parts.append(f'scale({scale})')
                if transform_parts:
                    attributes_str += ' transform="' + ' '.join(transform_parts) + '"'
    
            if element['tag'] == 'g':
                children_content = ''.join([self.process_element(child) for child in element.get('elements', [])])
                return f'<g {attributes_str}>\n{children_content}</g>\n'
            else:
                return f'<{element["tag"]} {attributes_str} />\n'
        else:
            print(f"Error: Element is not a dictionary. Received: {element}")
            return ""  # Retourner une chaîne vide en cas d'erreur pour éviter de corrompre le SVG

    
    def update_svg_content(self):
        # Mise à jour ou ajout des attributs de largeur et de hauteur
        if self.width and self.height:
            if 'width="' in self.header:
                self.header = re.sub(r'width="[^"]*"', f'width="{self.width}{self.unit}"', self.header)
            else:
                self.header = self.header.rstrip('>\n') + f' width="{self.width}{self.unit}">\n'
            
            if 'height="' in self.header:
                self.header = re.sub(r'height="[^"]*"', f'height="{self.height}{self.unit}"', self.header)
            else:
                self.header = self.header.rstrip('>\n') + f' height="{self.height}{self.unit}">\n'
        
        # Mise à jour ou ajout de la viewBox
        if self.viewBox:
            new_viewBox_str = ' '.join(map(str, self.viewBox))
            if 'viewBox="' in self.header:
                self.header = re.sub(r'viewBox="[^"]*"', f'viewBox="{new_viewBox_str}"', self.header)
            else:
                self.header = self.header.rstrip('>\n') + f' viewBox="{new_viewBox_str}">\n'
        
        svg_elements_content = ''.join([self.process_element(element) for element in self.elements])
        self.content = f'{self.header}\n{svg_elements_content}</svg>'

    
    def px_to_mm(self, px):
        return px * 25.4 / self.ppi
    
    def mm_to_px(self, mm):
        return mm * self.ppi / 25.4
    
    def generate_svg_file(self, output_file):
        """
        Génère un fichier SVG à partir de l'instance SVG actuelle.
        
        Args:
            output_file (str): Chemin vers le fichier de sortie.
        """
        self.update_svg_content()  # Assurez-vous que self.content est à jour
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(self.content)
        print(f"SVG saved at {os.path.abspath(output_file)}")

def main():
    # Exemple d'utilisation
    output_path = '../examples/outputs'
    svg_content = read_svg('../static/images/network.svg')
    svg = SVG(svg_content)
    print(f"Largeur: {svg.width}{svg.unit}, Hauteur: {svg.height}{svg.unit}")
    svg.generate_svg_file(os.path.join(output_path, 'test_mm.svg'))
    
    svg.convert_units('px')
    svg.generate_svg_file(os.path.join(output_path, 'test_px.svg'))
    
    svg.add_element("rect", {"x": "10", "y": "10", "width": "80", "height": "80", "stroke": "black", "fill": "transparent"}, {"translate": (0, 0), "scale": 1})
    svg.generate_svg_file(os.path.join(output_path, 'test_mm_rect.svg'))
    
if __name__ == "__main__":
    main()
