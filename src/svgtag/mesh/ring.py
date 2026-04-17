"""Ring mesh generation and text wrapping."""
import numpy as np
import trimesh


def wrap_around(mesh):
    """
    Wrap flat mesh around cylindrical surface.
    Legacy implementation using subdivide + polar transformation.
    
    Args:
        mesh: Flat mesh to wrap
    
    Returns:
        Wrapped mesh
    """
    mesh.subdivide()
    x = mesh.vertices[:, 0]
    y = mesh.vertices[:, 1]
    z = mesh.vertices[:, 2]
    y_min = min(y)
    mesh.vertices = np.column_stack(
        (-y * np.cos(x / y_min + np.pi / 2), y * np.sin(x / y_min + np.pi / 2), z)
    )
    return mesh


def mesh_from_path(pathname, thickness):
    """
    Load SVG path and extrude to 3D mesh.
    Legacy function - prefer using svg_to_path2d + extrude_path.
    
    Args:
        pathname: Path to SVG file
        thickness: Extrusion thickness
    
    Returns:
        trimesh.Trimesh
    """
    with open(pathname, "rb") as file:
        path = trimesh.load_path(file, file_type="svg")
    
    poly = path.polygons_full
    # path = [trimesh.load_path(p.simplify(tolerance=0.1)) for p in poly]
    
    if isinstance(path, list):
        mesh = [p.extrude(thickness) for p in path]
    else:
        mesh = path.extrude(thickness)
    
    if isinstance(mesh, list):
        mesh = trimesh.boolean.union(mesh)
    
    return mesh


def revolve_ring(contour_vertices, sections=64):
    """
    Create ring mesh by revolving contour.
    
    Args:
        contour_vertices: (N, 2) array of (x, y) points
        sections: Number of revolution sections
    
    Returns:
        trimesh.Trimesh
    """
    mesh = trimesh.creation.revolve(contour_vertices, sections=sections)
    mesh.visual.face_colors = [240, 240, 240, 240]
    return mesh


def create_ring_with_text(ring_mesh, text_mesh, brand_mesh=None):
    """
    Assemble ring by subtracting text (and optional brand) from base ring.
    
    Args:
        ring_mesh: Base ring mesh
        text_mesh: Text mesh to subtract
        brand_mesh: Optional brand mesh to subtract
    
    Returns:
        Final ring mesh
    """
    result = trimesh.boolean.difference([ring_mesh, text_mesh])
    
    if brand_mesh is not None:
        result = trimesh.boolean.difference([result, brand_mesh])
    
    return result