import os
from SVGprocess import SVG

def shape_svg(width, height, thk, shape, hole):
    svg = SVG()  # Créer un nouvel objet SVG
    x0 = 0
    y0 = 0

    svg.height = height
    if hole == 0:
        svg.width = width
        svg.viewBox = [0, 0, width, height]
        # Ajout d'un rectangle directement à l'objet SVG
        svg.add_element('rect', {
            'x': x0,
            'y': y0,
            'width': width,
            'height': height,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': thk
        })
    else:
        svg.width = width + height / 2
        svg.viewBox = [- height / 2 , 0, width + height / 2, height]
        path_d = f"M {x0} {y0} h {width} v {height} h {-width} "
        if shape == 'rectangle':
            path_d += f"h {-height/2} v {-height} h {height/2} "
        elif shape == 'circle':
            path_d += f"a {height/2} {height/2} 0 0 1 {0} {-height} "
        elif shape == 'triangle':
            path_d += f"l {-height/2} {-height/2} l {height/2} {-height/2} "
        path_d += "z"

        # Ajout du path directement à l'objet SVG
        svg.add_element('path', {
            'd': path_d,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': thk
        })

        cx = - hole - thk / 2
        cy = height / 2

        # Ajout d'un cercle directement à l'objet SVG
        svg.add_element('circle', {
            'cx': cx,
            'cy': cy,
            'r': hole / 2,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': thk
        })
    
    svg.update_svg_content()
    return svg

def main():
    output_path = '../examples/outputs'
    width_mm = 80
    height_mm = 35
    thk = 1
    shape = 'circle'
    phi = 5
    
    # Appeler shape_svg pour créer l'objet SVG
    svg = shape_svg(width_mm, height_mm, thk, shape, phi)
    
    # Définir les propriétés du SVG
    svg.unit = 'mm'
    
    # Générer le fichier SVG
    svg.generate_svg_file(os.path.join(output_path, 'shape.svg'))

if __name__ == "__main__":
    main()
