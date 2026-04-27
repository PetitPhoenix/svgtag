"""
Debug script for testing view_mesh / orient_meshes rotations.
Uses a colored asymmetric box to verify view orientations.

Face colors (OpenGL native):
    -X: rouge    +X: vert
    -Y: bleu     +Y: jaune
    -Z: magenta  +Z: cyan

Three tests:
    Test 1 — OpenGL mesh, OpenGL view (native trimesh)
    Test 2 — OpenGL mesh, Physical view (interpret 'front' as physical, no conversion)
    Test 3 — Physical mesh (converted first), Physical view
"""
import numpy as np
from pathlib import Path
import trimesh
from svgtag.mesh.assembly import create_scene, orient_meshes


HERE = Path(__file__).resolve().parent
output_path = HERE / "outputs" / Path(__file__).stem
output_path.mkdir(parents=True, exist_ok=True)


def create_debug_mesh():
    """
    Asymmetric colored box for rotation debugging.
    Extents: X=10, Y=3, Z=6 — offset: [2, 1, 4]

    Face colors are set in OpenGL native convention.
    """
    box = trimesh.creation.box(extents=[10, 3, 6])
    box.apply_translation([2, 1, 4])
    colors = np.array([
        [255, 0,   0,   255],  # Face 0:  -X rouge
        [0,   0,   255, 255],  # Face 1:  -Y bleu
        [255, 0,   0,   255],  # Face 2:  -X rouge
        [255, 0,   255, 255],  # Face 3:  -Z magenta
        [0,   255, 255, 255],  # Face 4:  +Z cyan
        [0,   0,   255, 255],  # Face 5:  -Y bleu
        [0,   255, 255, 255],  # Face 6:  +Z cyan
        [255, 255, 0,   255],  # Face 7:  +Y jaune
        [255, 0,   255, 255],  # Face 8:  -Z magenta
        [255, 255, 0,   255],  # Face 9:  +Y jaune
        [0,   255, 0,   255],  # Face 10: +X vert
        [0,   255, 0,   255],  # Face 11: +X vert
    ])
    box.visual.face_colors = colors
    return box


def save_scene_png(scene, output_path, prefix, view, tilt, rot):
    """Save scene as PNG."""
    filename = f"{prefix}_{view}_t{tilt:03d}_r{rot:03d}.png"
    filepath = output_path / filename
    png = scene.save_image(resolution=[1920, 1080], smooth=False)
    with open(filepath, 'wb') as f:
        f.write(png)
    print(f"  ✓ {filename}")


# --- Parameters ---
tilt  = 0
rot   = 30
views = ['front', 'back', 'top', 'bottom', 'left', 'right']

debug = create_debug_mesh()
# debug.show(smooth=False, flags={'wireframe': True, 'axis': True})

# ============================================================================
# Test 1: OpenGL mesh, OpenGL view (native trimesh)
# ============================================================================
# Expected:
#   front  → +z cyan
#   back   → -z magenta
#   top    → +y jaune
#   bottom → -y bleu
#   left   → -x rouge
#   right  → +x vert
print("\n=== Test 1: OpenGL mesh, OpenGL view ===")
for view in views:
    scene = create_scene(
        [debug], materials=None,
        view=view, tilt=tilt, rot=rot,
        convention='opengl',
    )
    save_scene_png(scene, output_path, "test1_opengl", view, tilt, rot)


# ============================================================================
# Test 2: OpenGL mesh, Physical view (no conversion of mesh)
# ============================================================================
# Mesh stays in OpenGL coordinates, but we interpret 'view' in physical sense:
#   front (physical -Y) → looks at face -y of mesh = bleu
#   back  (physical +Y) → +y = jaune
#   top   (physical +Z) → +z = cyan
#   bottom(physical -Z) → -z = magenta
#   left  (physical -X) → -x = rouge
#   right (physical +X) → +x = vert
print("\n=== Test 2: OpenGL mesh, Physical view (no conversion) ===")
for view in views:
    scene = create_scene(
        [debug], materials=None,
        view=view, tilt=tilt, rot=rot,
        convention='physical',
    )
    save_scene_png(scene, output_path, "test2_mixed", view, tilt, rot)


# ============================================================================
# Test 3: Physical mesh (converted), Physical view
# ============================================================================
# We rotate the mesh OpenGL -> Physical (rotation +pi/2 around X).
# After conversion, colors migrate to new coordinates:
#   -y opengl (bleu)    -> +Z physical
#   +y opengl (jaune)   -> -Z physical
#   +z opengl (cyan)    -> -Y physical
#   -z opengl (magenta) -> +Y physical
#   +/-x unchanged
#
# Expected with physical view:
#   front  (-Y) -> cyan
#   back   (+Y) -> magenta
#   top    (+Z) -> bleu
#   bottom (-Z) -> jaune
#   left   (-X) -> rouge
#   right  (+X) -> vert
print("\n=== Test 3: Physical mesh (converted), Physical view ===")
debug_physical = orient_meshes([debug], source='opengl', target='physical')[0]
# debug_physical.show(smooth=False, flags={'wireframe': True, 'axis': True})

for view in views:
    scene = create_scene(
        [debug_physical], materials=None,
        view=view, tilt=tilt, rot=rot,
        convention='physical',
    )
    save_scene_png(scene, output_path, "test3_physical", view, tilt, rot)


# Interactive debug (uncomment to use):
# scene = create_scene([debug], materials=None, view='front', convention='opengl')
# scene.show(smooth=False, flags={'wireframe': True, 'axis': True})

print(f"\nAll tests done. PNG output in {output_path}")