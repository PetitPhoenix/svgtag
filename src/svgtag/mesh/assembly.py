"""3D mesh assembly utilities"""
import os
import trimesh
import numpy as np


def assemble_plate(shape_mesh, face_meshes):
    """
    Assemble a plate by subtracting face meshes from shape.
    
    Args:
        shape_mesh: Base shape mesh
        face_meshes: List of face meshes to subtract
    
    Returns:
        Final plate mesh
    """
    if not face_meshes:
        return shape_mesh
    
    # Filter valid meshes
    valid_faces = []
    for face_mesh in face_meshes:
        try:
            if hasattr(face_mesh, 'is_volume') and face_mesh.is_volume:
                valid_faces.append(face_mesh)
            else:
                print(f"  Warning: Skipping non-volume face mesh")
        except:
            print(f"  Warning: Could not check face mesh validity")
    
    if not valid_faces:
        print("  Warning: No valid face meshes, returning shape only")
        return shape_mesh
    
    # Union all face meshes
    try:
        if len(valid_faces) == 1:
            negative = valid_faces[0]
        else:
            negative = valid_faces[0]
            for face_mesh in valid_faces[1:]:
                try:
                    negative = negative.union(face_mesh)
                except:
                    print(f"  Warning: Could not union face mesh, concatenating")
                    negative = trimesh.util.concatenate([negative, face_mesh])
    except Exception as e:
        print(f"  Warning: Face union failed: {e}, using first mesh only")
        negative = valid_faces[0]
    
    # Subtract from shape
    try:
        plate = trimesh.boolean.difference([shape_mesh, negative])
    except Exception as e:
        print(f"  Warning: Boolean difference failed: {e}, returning shape")
        return shape_mesh
    
    return plate


def create_scene(meshes, colors=None, camera_distance=75):
    """
    Create a trimesh Scene with meshes and colors.
    
    Args:
        meshes: List of trimesh meshes [plate, face_A, face_B, ...]
        colors: List of RGB colors [[48,48,48], [248,248,241], ...]
        camera_distance: Camera distance multiplier
    
    Returns:
        trimesh.Scene
    """
    if colors is None:
        # Default colors: dark gray for plate, off-white for text
        colors = [
            [48, 48, 48, 255],  # Plate (dark gray)
            [248, 248, 241, 255],  # Face A (off-white)
            [248, 248, 241, 255],  # Face B (off-white)
        ]
    
    # Create scene
    scene = trimesh.Scene()
    
    # Add meshes with materials
    material = trimesh.visual.material.SimpleMaterial(
        diffuse=[0.8, 0.8, 0.8],
        ambient=[1, 1, 1],
        specular=None,
        glossiness=1
    )
    
    for i, mesh in enumerate(meshes):
        mesh.visual.material = material
        if i < len(colors):
            mesh.visual.face_colors = colors[i]
        scene.add_geometry(mesh)
    
    # Camera transform
    R = trimesh.transformations.concatenate_matrices(
        trimesh.transformations.rotation_matrix(angle=-np.pi / 3, direction=[1, 0, 0]),
        trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1]),
    )
    R[0:3, 3] = [0, 3 * camera_distance, 3 * 3]
    scene.camera_transform = R
    
    return scene


def export_stl(meshes, output_path, names=['mesh.stl', 'side_A.stl', 'side_B.stl']):
    """
    Export meshes to STL files.
    
    Args:
        meshes: List of meshes
        output_path: Output directory
        names: List of filenames
    """
    os.makedirs(output_path, exist_ok=True)
    
    for mesh, name in zip(meshes, names):
        filepath = os.path.join(output_path, name)
        mesh.export(filepath)
        print(f"✓ {name}")
    
    print(f"\nSTL files saved in {os.path.abspath(output_path)}")