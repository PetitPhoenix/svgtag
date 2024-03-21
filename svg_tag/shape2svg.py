from text2svg import generate_svg
import os

def shape_svg(width, height, thk, shape, hole):
    elements = []
    x0 = height / 2 if hole > 0 else 0
    y0 = 0

    if hole == 0:
        elements.append(f'<rect x="{x0}" y="{y0}" width="{width}" height="{height}" fill="none" stroke="black" stroke-width="{thk}"/>')
    else:
        path_d = f"M {x0} {y0} h {width} v {height} h {-width} "
        if shape == 'rectangle':
            path_d += f"h {-height/2} v {-height} h {height/2} "
        elif shape == 'circle':
            path_d += f"a {height/2} {height/2} 0 0 1 {0} {-height} "
        elif shape == 'triangle':
            path_d += f"l {-height/2} {-height/2} l {height/2} {-height/2} "
        path_d += "z"
        elements.append(f'<path d="{path_d}" fill="none" stroke="black" stroke-width="{thk}"/>')

        cx = 2 * hole + thk / 2
        cy = height / 2
        elements.append(f'<circle cx="{cx}" cy="{cy}" r="{hole / 2}" fill="none" stroke="black" stroke-width="{thk}"/>')

    return elements

def main():
    output_path = '../examples/outputs'
    width_mm = 80
    height_mm = 35
    thk = 1
    shape = 'rectangle'
    phi = 5
    loc_vis = [0, 0, width_mm + height_mm / 2 if phi > 0 else width_mm, height_mm]
    svg_shape = shape_svg(width_mm, height_mm, thk, shape, phi)
    generate_svg(svg_shape, os.path.join(output_path, 'shape.svg'), loc_vis)

if __name__ == "__main__":
    main()
