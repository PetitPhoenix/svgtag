"""3D mesh visualization utilities"""
import os
import trimesh
import numpy as np


# ============================================================================
# Conventions
# ============================================================================
# OpenGL  : x droite, y haut,  z vers caméra
# Physique: X droite, Y profondeur (s'éloigne), Z haut
# ============================================================================


# ============================================================================
# Convention conversion
# ============================================================================

def orient_meshes(meshes, source='opengl', target='opengl'):
    """
    Convert meshes between OpenGL and Physical conventions.

    OpenGL   : x right, y up,         z toward camera
    Physical : X right, Y depth away, Z up

    Transformations:
        opengl   → physical : rotation +π/2 around X  (y→z, z→-y)
        physical → opengl   : rotation -π/2 around X  (z→y, y→-z)

    Args:
        meshes: List of trimesh meshes
        source: Convention of input meshes ('opengl' or 'physical')
        target: Desired convention ('opengl' or 'physical')

    Returns:
        List of converted mesh copies (no-op if source == target)
    """
    oriented = [m.copy() for m in meshes]

    if source == target:
        return oriented

    all_verts = np.vstack([m.vertices for m in oriented])
    pivot = (all_verts.min(axis=0) + all_verts.max(axis=0)) / 2

    if source == 'opengl' and target == 'physical':
        angle = np.pi / 2
    elif source == 'physical' and target == 'opengl':
        angle = -np.pi / 2
    else:
        raise ValueError(f"Unsupported conversion: {source} → {target}")

    mat = trimesh.transformations.rotation_matrix(angle, [1, 0, 0], pivot)
    for mesh in oriented:
        mesh.apply_transform(mat)

    return oriented


# ============================================================================
# View selection
# ============================================================================

def view_mesh(meshes, view='front', tilt=0, rot=0, convention='opengl'):
    """
    Orient meshes so that the requested face arrives toward the default camera.

    The camera is fixed (looks toward -z OpenGL).
    We rotate the mesh to bring the desired face into view.

    Convention 'opengl' (default trimesh native):
        front  → face +z (toward camera)
        back   → face -z
        top    → face +y
        bottom → face -y
        left   → face -x
        right  → face +x

    Convention 'physical':
        front  → face -Y (toward viewer)
        back   → face +Y
        top    → face +Z
        bottom → face -Z
        left   → face -X
        right  → face +X

    Args:
        meshes:     List of trimesh meshes (assumed to be in `convention`)
        view:       'front', 'back', 'top', 'bottom', 'left', 'right'
        tilt:       Tilt angle in degrees (around horizontal screen axis)
        rot:        Rotation angle in degrees (around view axis)
        convention: 'opengl' or 'physical'

    Returns:
        List of oriented mesh copies
    """
    oriented = [m.copy() for m in meshes]

    all_verts = np.vstack([m.vertices for m in oriented])
    pivot = (all_verts.min(axis=0) + all_verts.max(axis=0)) / 2

    if convention == 'opengl':
        view_base = _view_base_opengl(pivot)
    elif convention == 'physical':
        view_base = _view_base_physical(pivot)
    else:
        raise ValueError(f"Unknown convention: {convention}")

    # Tilt and rotation: applied in screen space (after view_base)
    rot_mat  = trimesh.transformations.rotation_matrix(np.radians(rot),  [0, 1, 0], pivot)
    tilt_mat = trimesh.transformations.rotation_matrix(np.radians(tilt), [1, 0, 0], pivot)

    for mesh in oriented:
        mesh.apply_transform(view_base[view])
        mesh.apply_transform(rot_mat)
        mesh.apply_transform(tilt_mat)

    return oriented


def _view_base_opengl(pivot):
    """
    View base rotations for OpenGL convention.
    Camera looks from +z toward -z, with +y screen up.
    """
    rm = trimesh.transformations.rotation_matrix
    return {
        'front':  np.eye(4),                          # see +z (toward camera by default)
        'back':   rm(np.pi,     [0, 1, 0], pivot),    # rotate 180° around y → see -z
        'top':    rm( np.pi/2,  [1, 0, 0], pivot),    # see +y
        'bottom': rm(-np.pi/2,  [1, 0, 0], pivot),    # see -y
        'left':   rm( np.pi/2,  [0, 1, 0], pivot),    # see -x
        'right':  rm(-np.pi/2,  [0, 1, 0], pivot),    # see +x
    }


def _view_base_physical(pivot):
    """
    View base rotations for Physical convention.
    Camera still looks from +z toward -z (default trimesh camera),
    so we need to bring the physical face to +z.

    Physical → screen mapping for each view:
        front  : -Y → +z   (rotation +π/2 around X: -y → +z)
        back   : +Y → +z   (rotation -π/2 around X)
        top    : +Z → +z   (already aligned, no rotation needed)
        bottom : -Z → +z   (rotation π around X)
        left   : -X → +z   (rotation +π/2 around Y? no, around Y: x → ±z)
        right  : +X → +z   (rotation -π/2 around Y)
    """
    rm = trimesh.transformations.rotation_matrix
    return {
        'front':  rm(-np.pi/2, [1, 0, 0], pivot),                          # -Y → +z, +Z → +y
        'back':   rm(-np.pi/2, [1, 0, 0], pivot)
                @ rm( np.pi,   [0, 0, 1], pivot),                          # +Y → +z, +Z → +y
        'top':    np.eye(4),                                               # +Z → +z (already)
        'bottom': rm( np.pi,   [1, 0, 0], pivot),                          # -Z → +z
        'left':   rm( np.pi/2, [0, 0, 1], pivot)
                @ rm( np.pi/2, [0, 1, 0], pivot),                          # -X → +z, +Z → +y
        'right':  rm(-np.pi/2, [0, 0, 1], pivot)
                @ rm(-np.pi/2, [0, 1, 0], pivot),                          # +X → +z, +Z → +y
    }


def create_scene(meshes, colors=None, view='front', tilt=0, rot=0,
                 convention='opengl'):
    """
    Create a trimesh Scene with oriented meshes and optional materials.

    The meshes are NOT converted between conventions.
    `convention` only tells how to interpret `view` (which face is 'front', etc.).

    If you need to convert your meshes to a different convention first,
    call `orient_meshes(meshes, source=..., target=...)` explicitly before
    passing them here.

    Args:
        meshes:     List of trimesh meshes
        colors: List of RGBA tuples (one per mesh), e.g. [(48,48,48,255), (248,248,241,255)]
        view:       'top', 'bottom', 'front', 'back', 'left', 'right'
        tilt:       Tilt angle in degrees
        rot:        Rotation angle in degrees
        convention: How to interpret `view` ('opengl' or 'physical')

    Returns:
        trimesh.Scene
    """
    oriented = view_mesh(meshes, view=view, tilt=tilt, rot=rot, convention=convention)

    scene = trimesh.Scene()
    for i, mesh in enumerate(oriented):
        if colors is not None and i < len(colors):
            mesh.visual.face_colors = colors[i]
        scene.add_geometry(mesh)
    return scene


# ============================================================================
# Export
# ============================================================================

def export_html(scene, output_path):
    """
    Export a trimesh Scene to a standalone HTML file with three.js viewer.

    Mirrors the approach of trimesh's native viewer:
    - Single directional light (no ambient) for clean shading without artifacts
    - Camera embedded in the GLB
    - Materials from the GLB are kept as-is (no override)

    Args:
        scene:       trimesh.Scene
        output_path: Path to output HTML file
    """
    import base64

    bounds = scene.bounds
    center = bounds.mean(axis=0)
    max_ext = (bounds[1] - bounds[0]).max()
    distance = max_ext * 2.0

    ex, ey, ez = center + np.array([0, 0, distance])
    cx, cy, cz = center

    gltf_bytes = scene.export(file_type='glb')
    gltf_b64 = base64.b64encode(gltf_bytes).decode('utf-8')

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>body {{ margin: 0; overflow: hidden; background: #ffffff; }}</style>
</head>
<body>
<script type="importmap">
  {{"imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.158/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.158/examples/jsm/"
  }}}}
</script>
<script type="module">
  import * as THREE from 'three';
  import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
  import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffffff);

  // Single directional light that follows the camera (like trimesh native viewer)
  const light = new THREE.DirectionalLight(0xffffff, 1.5);
  scene.add(light);

  const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.01, 100000);
  camera.position.set({ex:.4f}, {ey:.4f}, {ez:.4f});
  camera.up.set(0, 1, 0);
  camera.lookAt({cx:.4f}, {cy:.4f}, {cz:.4f});

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set({cx:.4f}, {cy:.4f}, {cz:.4f});
  controls.update();

  const b64 = "{gltf_b64}";
  const binary = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const blob = new Blob([binary], {{type: 'application/octet-stream'}});
  const url = URL.createObjectURL(blob);
  new GLTFLoader().load(url, gltf => {{
    scene.add(gltf.scene);
    URL.revokeObjectURL(url);
  }});

  window.addEventListener('resize', () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }});

  function animate() {{
    requestAnimationFrame(animate);
    controls.update();
    light.position.copy(camera.position);  // light follows camera
    renderer.render(scene, camera);
  }}
  animate();
</script>
</body>
</html>"""

    with open(output_path, 'w') as f:
        f.write(html)


def export_stl(meshes, output_path, names=['mesh.stl', 'side_A.stl', 'side_B.stl']):
    """
    Export meshes to STL files.

    Args:
        meshes:       List of meshes
        output_path:  Output directory
        names:        List of filenames
    """
    os.makedirs(output_path, exist_ok=True)

    for mesh, name in zip(meshes, names):
        filepath = os.path.join(output_path, name)
        mesh.export(filepath)
        print(f"✓ {name}")

    print(f"\nSTL files saved in {os.path.abspath(output_path)}")
