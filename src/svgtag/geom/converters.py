"""Conversions entre Shapely, SVG et mesh"""
from ..svg.base import SVG
import trimesh


def to_svg_path(polygon):
    """Convertit un Polygon Shapely en path SVG avec trous"""
    path_d = ""
    
    # Extérieur (sens horaire)
    coords = list(polygon.exterior.coords)
    if coords:
        path_d += f"M {coords[0][0]:.3f} {coords[0][1]:.3f} "
        for x, y in coords[1:-1]:
            path_d += f"L {x:.3f} {y:.3f} "
        path_d += "Z "
    
    # Trous (sens anti-horaire pour SVG)
    for interior in polygon.interiors:
        coords = list(interior.coords)
        if coords:
            path_d += f"M {coords[0][0]:.3f} {coords[0][1]:.3f} "
            for x, y in coords[1:-1]:
                path_d += f"L {x:.3f} {y:.3f} "
            path_d += "Z "
    
    return path_d.strip()


def to_svg(geometry, width=None, height=None):
    """
    Convertit une géométrie Shapely en objet SVG
    
    Args:
        geometry: Polygon Shapely
        width, height: Dimensions du SVG (auto si None)
    
    Returns:
        SVG object
    """
    # Calculer les dimensions si non fournies
    if width is None or height is None:
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
    
    svg = SVG()
    svg.width = width
    svg.height = height
    svg.viewBox = [0, 0, width, height]
    svg.unit = "mm"
    
    path_d = to_svg_path(geometry)
    svg.add_element('path', {
        'd': path_d,
        'fill': 'none',
        'stroke': 'black',
        'stroke-width': 0.1
    })
    svg.update_svg_content()
    
    return svg


def to_mesh(geometry, thickness):
    """
    Convertit une géométrie Shapely en mesh 3D
    
    Args:
        geometry: Polygon Shapely
        thickness: Épaisseur d'extrusion en mm
    
    Returns:
        trimesh.Trimesh
    """
    # Utiliser extrude_polygon de trimesh
    mesh = trimesh.creation.extrude_polygon(geometry, thickness)
    return mesh