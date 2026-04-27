"""Trimesh material presets for 3D visualization."""
import trimesh


def simple_material(color_rgba, glossiness=1.0, doubleSided=True):
    """
    Create a SimpleMaterial with a flat color.

    Args:
        color_rgba:   [R, G, B, A] 0-255
        glossiness:   float
        doubleSided:  bool

    Returns:
        trimesh.visual.material.SimpleMaterial
    """
    r, g, b, a = [c / 255.0 for c in color_rgba]
    mat = trimesh.visual.material.SimpleMaterial(
        diffuse=[r, g, b, a],
        ambient=[1, 1, 1, 1],
        specular=None,
        glossiness=glossiness,
    )
    mat.doubleSided = doubleSided
    return mat


# --- Presets ---

# Tag / plate
DARK_GRAY   = [48,  48,  48,  255]
OFF_WHITE   = [248, 248, 241, 255]

# Debug
RED         = [255, 0,   0,   255]
GREEN       = [0,   255, 0,   255]
BLUE        = [0,   0,   255, 255]
YELLOW      = [255, 255, 0,   255]
CYAN        = [0,   255, 255, 255]
MAGENTA     = [255, 0,   255, 255]