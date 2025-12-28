"""Formes géométriques de base"""
from shapely.geometry import Polygon, Point, LinearRing
from shapely.ops import unary_union
import numpy as np


def rectangle(width, height, x=0, y=0):
    """Crée un rectangle"""
    return Polygon([
        (x, y), (x + width, y),
        (x + width, y + height), (x, y + height)
    ])


def circle(radius, center_x=0, center_y=0, num_points=64):
    """Crée un cercle"""
    return Point(center_x, center_y).buffer(radius, resolution=num_points//4)


def rounded_rectangle(width, height, corner_radius, x=0, y=0):
    """Rectangle avec coins arrondis"""
    rect = rectangle(width, height, x, y)
    return rect.buffer(-corner_radius).buffer(corner_radius)


def add_hole(geometry, hole_diameter, hole_x, hole_y):
    """
    Ajoute un trou à une géométrie
    
    Args:
        geometry: Polygon Shapely
        hole_diameter: Diamètre du trou
        hole_x, hole_y: Position du centre du trou
    
    Returns:
        Polygon avec trou
    """
    hole = circle(hole_diameter / 2, hole_x, hole_y)
    return geometry.difference(hole)


def tag_circle(width, height):
    """
    Tag avec forme circulaire à gauche (demi-cercle + rectangle)
    
    Args:
        width: Largeur du rectangle principal
        height: Hauteur totale
    
    Returns:
        Polygon Shapely
    """
    # Rectangle principal
    rect = rectangle(width, height, x=0, y=0)
    
    # Demi-cercle à gauche
    radius = height / 2
    half_circle = circle(radius, center_x=0, center_y=radius)
    
    # Découper pour ne garder que la partie gauche
    cutting_rect = rectangle(radius, height * 2, x=-radius, y=-height/2)
    half_circle = half_circle.intersection(cutting_rect)
    
    # Union
    return unary_union([rect, half_circle])


def tag_rectangle(width, height, corner_radius=0):
    """
    Tag rectangulaire simple
    
    Args:
        width: Largeur
        height: Hauteur
        corner_radius: Rayon des coins arrondis (0 = coins carrés)
    
    Returns:
        Polygon Shapely
    """
    if corner_radius > 0:
        return rounded_rectangle(width, height, corner_radius)
    return rectangle(width, height)

def tag_triangle(width, height, side='left'):
    """
    Tag avec triangle pointu
    
    Args:
        width: Largeur du rectangle principal
        height: Hauteur totale
        side: 'left' ou 'right' - côté où se trouve la pointe
    
    Returns:
        Polygon Shapely
    """
    # Rectangle principal
    rect = rectangle(width, height, x=0, y=0)
    
    # Triangle pointu
    if side == 'left':
        # Pointe vers la gauche
        triangle = Polygon([
            (0, 0),
            (-height/2, height/2),
            (0, height)
        ])
    else:
        # Pointe vers la droite
        triangle = Polygon([
            (width, 0),
            (width + height/2, height/2),
            (width, height)
        ])
    
    # Union
    return unary_union([rect, triangle])


def tablet_with_ear(width, height, padding, eyelet_outer_diameter, eyelet_hole_diameter, ear_offset=[0, 0]):
    """
    Plaque avec oreille (rectangle coins arrondis + œillet)
    
    Args:
        width, height: Dimensions de la plaque (rectangle principal)
        padding: Rayon des coins arrondis
        eyelet_outer_diameter: Diamètre extérieur de l'œillet
        eyelet_hole_diameter: Diamètre du trou central
        ear_offset: [offset_x, offset_y] en mm depuis le coin bas-gauche
                   [0, 0] = oreille centrée sur le coin (dépasse de radius)
                   [-5, -5] = oreille décalée vers extérieur
                   [5, 5] = oreille décalée vers intérieur
    
    Returns:
        Polygon Shapely
    """
    # Rectangle avec coins arrondis
    rect = rounded_rectangle(width, height, padding)
    
    # Position de l'œillet (depuis le coin bas-gauche du rectangle)
    eyelet_x = ear_offset[0]
    eyelet_y = ear_offset[1]
    
    # Cercle extérieur de l'œillet
    eyelet_outer = circle(eyelet_outer_diameter / 2, eyelet_x, eyelet_y)
    
    # Union rectangle + œillet extérieur
    shape = unary_union([rect, eyelet_outer])
    
    # Soustraire le trou central de l'œillet
    eyelet_hole = circle(eyelet_hole_diameter / 2, eyelet_x, eyelet_y)
    shape = shape.difference(eyelet_hole)
    
    return shape



def circle_profile(height, R_out, R_ins, side, num_points):
    """
    Generate circular profile for ring cross-section.
    
    Args:
        height: Ring height
        R_out: Outer radius
        R_ins: Inner radius
        side: 1 for outer, -1 for inner
        num_points: Number of points
    
    Returns:
        Array of (x, y) points
    """
    shift = 0
    # Radius on the x-axis
    a = ((height / 2) ** 2 + (R_out - R_ins) ** 2) / (2 * (R_out - R_ins))
    # Radius on the y-axis
    b = a
    alpha = np.arcsin((height / 2) / a)
    # x-position of the center
    if side == 1:
        u = R_out - a
    else:
        u = R_ins + a
        shift = +np.pi
    # y-position of the center
    v = 0
    t = np.linspace(-alpha, alpha, 2 ** int(num_points / 4))
    x = u + a * np.cos(t + shift)
    y = v + b * np.sin(t + shift)
    return np.transpose([x, y])


def ellipse_profile(height, R_out, R_ins, side, num_points):
    """
    Generate elliptical profile for ring cross-section.
    
    Args:
        height: Ring height
        R_out: Outer radius
        R_ins: Inner radius
        side: 1 for outer, -1 for inner
        num_points: Number of points
    
    Returns:
        Array of (x, y) points
    """
    shift = 0
    # Radius on the x-axis
    a = R_out - R_ins
    # Radius on the y-axis
    b = height / 2
    # x-position of the center
    if side == 1:
        u = R_ins
    else:
        u = R_out
        shift = +np.pi
    # y-position of the center
    v = 0
    t = np.linspace(-np.pi / 2, np.pi / 2, 2 ** int(num_points / 4))
    x = u + a * np.cos(t + shift)
    y = v + b * np.sin(t + shift)
    return np.transpose([x, y])


def ring_contour(height, R_ext, R_med, R_int, num_points, profile_type='circle'):
    """
    Generate ring contour (vertices and faces for revolution).
    
    Args:
        height: Ring height
        R_ext: External radius
        R_med: Medium radius (text depth)
        R_int: Internal radius
        num_points: Resolution
        profile_type: 'circle' or 'ellipse'
    
    Returns:
        (vertices, faces) for trimesh revolution
    """
    if profile_type == 'circle':
        external = circle_profile(height, R_ext, R_med, +1, num_points)
        internal = circle_profile(height, R_med, R_int, -1, num_points)
    elif profile_type == 'ellipse':
        external = ellipse_profile(height, R_ext, R_med, +1, num_points)
        internal = ellipse_profile(height, R_med, R_int, -1, num_points)
    else:
        raise ValueError(f"Unknown profile_type: {profile_type}")
    
    vertices = np.concatenate((external, internal))
    vertices = vertices[np.sort(np.unique(vertices, axis=0, return_index=True)[1])]
    vertices = np.column_stack((vertices, np.zeros(len(vertices))))
    vertices = np.vstack([vertices, vertices[0]])
    faces = np.roll(np.arange(len(vertices) + 1), 1)
    faces = np.hstack(faces)
    return vertices, faces