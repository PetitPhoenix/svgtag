"""SVG to 3D mesh extrusion utilities"""
import os
import trimesh
import tempfile
from .svg_helpers import prepare_for_trimesh_angles


def extrude_path(path2d, thickness):
    """
    Extrude a 2D path to create a 3D mesh.
    
    Args:
        path2d: trimesh.path.Path2D object
        thickness: Extrusion thickness in mm
    
    Returns:
        trimesh.Trimesh
    """
    mesh = path2d.extrude(thickness)
    
    if isinstance(mesh, list):
        try:
            # Try union first
            mesh = trimesh.boolean.union(mesh)
        except:
            # If union fails, concatenate
            print(f"  Warning: Boolean union failed, using concatenation ({len(mesh)} parts)")
            mesh = trimesh.util.concatenate(mesh)
    
    return mesh


def svg_to_path2d(svg, prepare=True):
    """
    Convert SVG object to trimesh Path2D.
    
    Args:
        svg: SVG object
        prepare: If True, prepare angles for trimesh
    
    Returns:
        trimesh.path.Path2D
    """
    if prepare:
        svg = prepare_for_trimesh_angles(svg)
    
    # Save to temp file
    svg.update_svg_content()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8') as tmp:
        tmp.write(svg.content)
        tmp_path = tmp.name
    
    # Load with trimesh
    with open(tmp_path, 'rb') as f:
        path2d = trimesh.load_path(f, file_type='svg')
    
    # Cleanup
    os.unlink(tmp_path)
    
    return path2d