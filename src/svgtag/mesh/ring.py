"""Ring mesh generation and text wrapping."""
import numpy as np
import trimesh


def wrap_around(mesh, theta=np.pi/2):
    """
    Wrap flat mesh around cylindrical surface.
    
    Args:
        mesh:  Flat mesh to wrap (X=angular, Y=radius, Z=height)
        theta: Starting angle on cylinder (default π/2 = +Y face)
               π/2  → face +Y (back)
              -π/2  → face -Y (front)
               0    → face +X (right)
               etc.
    Returns:
        Wrapped mesh
    """
    mesh.subdivide()
    x = mesh.vertices[:, 0]
    y = mesh.vertices[:, 1]
    z = mesh.vertices[:, 2]
    y_min = min(y)
    mesh.vertices = np.column_stack(
        (-y * np.cos(x / y_min + theta),
          y * np.sin(x / y_min + theta), z)
    )
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