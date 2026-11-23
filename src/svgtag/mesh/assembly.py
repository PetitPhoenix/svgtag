"""3D mesh assembly utilities"""
import logging

import trimesh

logger = logging.getLogger(__name__)


def assemble_plate(shape_mesh, face_meshes):
    """
    Assemble a plate by subtracting face meshes from shape.

    Args:
        shape_mesh:   Base shape mesh
        face_meshes:  List of face meshes to subtract

    Returns:
        Final plate mesh
    """
    if not face_meshes:
        return shape_mesh

    valid_faces = []
    for face_mesh in face_meshes:
        try:
            if hasattr(face_mesh, 'is_volume') and face_mesh.is_volume:
                valid_faces.append(face_mesh)
            else:
                logger.warning("skipping non-volume face mesh")
        except Exception:
            logger.warning("could not check face mesh validity")

    if not valid_faces:
        logger.warning("no valid face meshes, returning shape only")
        return shape_mesh

    try:
        if len(valid_faces) == 1:
            negative = valid_faces[0]
        else:
            negative = valid_faces[0]
            for face_mesh in valid_faces[1:]:
                try:
                    negative = negative.union(face_mesh)
                except Exception:
                    logger.warning("could not union face mesh, concatenating")
                    negative = trimesh.util.concatenate([negative, face_mesh])
    except Exception as e:
        logger.warning("face union failed: %s, using first mesh only", e)
        negative = valid_faces[0]

    try:
        plate = trimesh.boolean.difference([shape_mesh, negative])
    except Exception as e:
        logger.warning("boolean difference failed: %s, returning shape", e)
        return shape_mesh

    return plate
