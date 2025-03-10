from .svgprocess import SVG

def shape_svg(width, height, thk, shape, hole=0):
    svg = SVG()  # Créer un nouvel objet SVG
    x0 = 0
    y0 = 0

    svg.height = height
    if hole == 0:
        svg.width = width
        svg.viewBox = [0, 0, width, height]
        # Ajout d'un rectangle directement à l'objet SVG
        # svg.add_element('rect', {
        #     'x': x0,
        #     'y': y0,
        #     'width': width,
        #     'height': height,
        #     'fill': 'none',
        #     'stroke': 'black',
        #     'stroke-width': thk
        # })
        path_d = f"M {x0} {y0} h {width} v {height} h {-width} v {-height} z"
        svg.add_element('path', {
            'd': path_d,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': thk
        })
        
    else:
        svg.width = width + height / 2
        svg.viewBox = [- height / 2 , 0, width + height / 2, height]
        path_d = f"M {x0} {y0} h {width} v {height} h {-width} "
        if shape == 'rectangle':
            path_d += f"v {-height} "
        elif shape == 'circle':
            path_d += f"a {height/2} {height/2} 0 0 1 {0} {-height} "
        elif shape == 'triangle':
            path_d += f"l {-height/2} {-height/2} l {height/2} {-height/2} "
        path_d += "z "

        cx = -hole - thk / 2
        cy = height / 2
        
        # Construction du chemin pour le trou (cercle)
        path_d += f"M {cx} {cy} "
        path_d += f"m {-hole / 2} 0 "
        path_d += f"a {hole / 2} {hole / 2} 0 1 1 {hole} 0 "
        path_d += f"a {hole / 2} {hole / 2} 0 1 1 {-hole} 0 z"

        # Ajout du path directement à l'objet SVG
        svg.add_element('path', {
            'd': path_d,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': thk
        })
    
    svg.update_svg_content()
    return svg