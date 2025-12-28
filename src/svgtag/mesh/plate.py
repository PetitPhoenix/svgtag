"""Conversion SVG → STL pour plaques"""
import os
import numpy as np
import trimesh
from .svg_helpers import prepare_for_trimesh_angles


def svg_to_stl(shape, thickness, output_path, side_A, side_B=None, brand=None):
    """
    Convertit des SVG en STL pour plaques multi-couleurs.
    
    Args:
        shape: Chemin vers SVG de la forme de base
        thickness: Épaisseur en mm (ex: 3)
        output_path: Dossier de sortie
        side_A: Chemin vers SVG du texte face A (recto)
        side_B: Chemin vers SVG du texte face B (verso) - optionnel
        brand: Si True, traite side_B comme un petit logo
    
    Returns:
        scene: Scène trimesh
    """
    
    os.makedirs(output_path, exist_ok=True)
    
    print("\n=== PRÉPARATION POUR TRIMESH ===")
    
    # Préparer les SVG (conversion des rotations pour trimesh)
    shape_prepared = os.path.join(output_path, "_shape_prepared.svg")
    side_A_prepared = os.path.join(output_path, "_side_A_prepared.svg")
    
    print("Shape:")
    prepare_for_trimesh_angles(shape, shape_prepared)
    print("Side A:")
    prepare_for_trimesh_angles(side_A, side_A_prepared)
    
    # 1. Forme de base
    with open(shape_prepared, "rb") as file:
        shape_svg = trimesh.load_path(file, file_type="svg")
    
    shape_mesh = shape_svg.extrude(thickness)

    # 2. Texte face A (recto)
    with open(side_A_prepared, "rb") as file:
        side_A_svg = trimesh.load_path(file, file_type="svg")
    
    # Épaisseur du texte : 2mm si recto seul, 1mm si recto-verso
    text_thickness_A = 1 if side_B else 2
    side_A_mesh = side_A_svg.extrude(text_thickness_A)
    side_A_mesh = trimesh.boolean.union(side_A_mesh)
    
    # Créer le négatif
    negative = side_A_mesh.copy()

    # 3. Face B (verso) - optionnelle
    if side_B:
        side_B_prepared = os.path.join(output_path, "_side_B_prepared.svg")
        print("Side B:")
        prepare_for_trimesh_angles(side_B, side_B_prepared)
        
        with open(side_B_prepared, "rb") as file:
            side_B_svg = trimesh.load_path(file, file_type="svg")
        
        side_B_mesh = side_B_svg.extrude(1)
        side_B_mesh = trimesh.boolean.union(side_B_mesh)
        
        # Rotation 180° autour X
        side_B_mesh = side_B_mesh.apply_transform(
            trimesh.transformations.rotation_matrix(angle=np.pi, direction=[1, 0, 0])
        )
        
        if brand:
            # Logo petit (comme l'ancien code)
            side_B_mesh = side_B_mesh.apply_transform(
                trimesh.transformations.scale_and_translate(
                    scale=[0.4, 0.4, 1],
                    translate=[
                        0.4 * shape_mesh.extents[0],
                        0.4 * shape_mesh.extents[1],
                        thickness,
                    ],
                )
            )
        else:
            # Verso pleine face
            side_B_mesh = side_B_mesh.apply_transform(
                trimesh.transformations.scale_and_translate(
                    scale=[1, 1, 1], 
                    translate=[0, shape_mesh.extents[1], thickness]
                )
            )
        
        # Ajouter au négatif
        negative = negative.union(side_B_mesh)

    # 4. Différence booléenne
    mesh = trimesh.boolean.difference([shape_mesh, negative])

    # 5. Créer la scène
    scene = trimesh.Scene()
    scene.add_geometry([mesh, side_A_mesh])
    if side_B:
        scene.add_geometry(side_B_mesh)

    # 6. Transformation caméra
    R = trimesh.transformations.concatenate_matrices(
        trimesh.transformations.rotation_matrix(angle=-np.pi / 3, direction=[1, 0, 0]),
        trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1]),
    )
    R[0:3, 3] = [0, 3 * 75, 3 * 3]
    scene.camera_transform = R

    # 7. Couleurs et matériaux
    material = trimesh.visual.material.SimpleMaterial(
        diffuse=[0.8, 0.8, 0.8], ambient=[1, 1, 1], specular=None, glossiness=1
    )
    
    mesh.visual.material = material
    side_A_mesh.visual.material = material
    mesh.visual.face_colors = [48, 48, 48, 255]
    side_A_mesh.visual.face_colors = [248, 248, 241, 255]
    
    if side_B:
        side_B_mesh.visual.material = material
        side_B_mesh.visual.face_colors = [248, 248, 241, 255]

    # 8. Export STL
    mesh.export(os.path.join(output_path, "mesh.stl"))
    side_A_mesh.export(os.path.join(output_path, "side_A.stl"))
    if side_B:
        side_B_mesh.export(os.path.join(output_path, "side_B.stl"))
    
    print(f"\n✓ STL saved at {os.path.abspath(output_path)}")

    return scene