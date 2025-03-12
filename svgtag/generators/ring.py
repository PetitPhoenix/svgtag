import os

import matplotlib.pyplot as plt
import numpy as np
import trimesh

from trimesh import viewer # if not written, error in import
from svgtag.generators.tag import tag

X = np.array([1, 0, 0])
Y = np.array([0, 1, 0])
Z = np.array([0, 0, 1])


def plot(data):
    fig, ax = plt.subplots(figsize=(2, 6))
    ax.plot(data[:, 0], data[:, 1], marker=".")
    ax.set_xlabel(r"Largeur [mm]", fontsize=10)
    ax.set_ylabel(r"Hauteur [mm]", fontsize=10)
    ax.set_title("Forme", fontsize=10)
    ax.grid(True)
    ax.axis("equal")
    # ax.set_aspect('equal', 'box')
    fig.tight_layout()
    plt.show()
    return fig, ax


def circle(height, R_out, R_ins, side, RES):
    shift = 0
    # radius on the x-axis
    a = ((height / 2) ** 2 + (R_out - R_ins) ** 2) / (2 * (R_out - R_ins))
    # radius on the y-axis
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
    t = np.linspace(-alpha, alpha, 2 ** np.int_(RES / 4))
    x = u + a * np.cos(t + shift)
    y = v + b * np.sin(t + shift)
    return np.transpose([x, y])


def ellipse(height, R_out, R_ins, side, RES):
    shift = 0
    # radius on the x-axis
    a = R_out - R_ins
    # radius on the y-axis
    b = height / 2
    # x-position of the center
    if side == 1:
        u = R_ins
    else:
        u = R_out
        shift = +np.pi
    # y-position of the center
    v = 0
    t = np.linspace(-np.pi / 2, np.pi / 2, 2 ** np.int_(RES / 4))
    x = u + a * np.cos(t + shift)
    y = v + b * np.sin(t + shift)
    return np.transpose([x, y])


def contour(HEIGHT, R_ext, R_med, R_int, RES, shape):
    if shape == 1:
        external = circle(HEIGHT, R_ext, R_med, +1, RES)
        internal = circle(HEIGHT, R_med, R_int, -1, RES)
    elif shape == 2:
        external = ellipse(HEIGHT, R_ext, R_med, +1, RES)
        internal = ellipse(HEIGHT, R_med, R_int, -1, RES)
    vertices = np.concatenate((external, internal))
    vertices = vertices[np.sort(np.unique(vertices, axis=0, return_index=True)[1])]
    vertices = np.column_stack((vertices, np.zeros(len(vertices))))
    vertices = np.vstack([vertices, vertices[0]])
    faces = np.roll(np.arange(len(vertices) + 1), 1)
    faces = np.hstack(faces)
    return vertices, faces


def gen3D(coords, RES=20, export=0, visu=0):
    mesh = trimesh.creation.revolve(coords, sections=int((RES / 4) ** 3))
    mesh.visual.face_colors = [240, 240, 240, 240]
    s = trimesh.Scene(mesh)

    if visu == 1:
        viewer.windowed.SceneViewer(s, start_loop=True)

    if export == 1:
        data = viewer.scene_to_html(s)
        return s, data
    elif export == 2:
        with open("data.html", "w") as file:
            file.write(viewer.scene_to_html(s))
    return s, mesh


def to_html(mesh):
    return viewer.scene_to_html(trimesh.Scene(mesh))


def export(mesh, style="html", path=None, name=None):
    scene = trimesh.Scene(mesh)
    if style == "scene":
        data = viewer.scene_to_html(scene)
        return scene, data
    elif style == "html":
        with open(os.path.join(path, name + ".html"), "w") as file:
            file.write(viewer.scene_to_html(scene))
        print(f"Scene saved to '{os.path.join(path, name + '.html')}'")
    elif style == "stl":
        # trimesh.exchange.stl.export_stl(mesh)
        mesh.export(os.path.join(path, name + ".stl"))
        print(f"Mesh saved to '{os.path.join(path, name + '.stl')}'")


def wrap_around(mesh):
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
    with open(pathname, "rb") as file:
        path = trimesh.load_path(file, file_type="svg")
        # path = trimesh.load_path(pathname)
    # txt_path = txt_path.simplify(tolerance = 0.2)
    poly = path.polygons_full
    path = [trimesh.load_path(p.simplify(tolerance=0.1)) for p in poly]
    if isinstance(path, list):
        mesh = [p.extrude(thickness) for p in path]
    else:
        mesh = path.extrude(thickness)
    if isinstance(mesh, list):
        mesh = trimesh.boolean.union(mesh)
    return mesh


def ring(
    text,
    diameter,
    height,
    thickness,
    res,
    font_dir,
    font,
    output_path,
    filename,
    shape=1,
    brand=True,
    vis=False,
):
    length = np.pi * (diameter - thickness)
    r = 0.25
    R_ext = diameter / 2
    R_int = R_ext - thickness
    R_med = R_int + r * thickness
    # Generate ring mesh
    vertices, faces = contour(height, R_ext, R_med, R_int, res, shape)
    if vis == True:
        plot(vertices)

    s, ring_mesh = gen3D(vertices[:, 0:2])

    outputname = os.path.join(output_path, filename + ".svg")
    text_tag = tag(
        text,
        os.path.join(font_dir, font),
        length,
        height,
        phi=None,
        shape=None,
        outline=False,
    )
    text_tag.generate_svg_file(outputname)

    # Generate text mesh
    txt_mesh = mesh_from_path(outputname, -thickness)
    txt_mesh = txt_mesh.apply_transform(
        trimesh.transformations.rotation_matrix(angle=-np.pi / 2, direction=[1, 0, 0])
    )
    txt_mesh = txt_mesh.apply_transform(
        trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1])
    )
    txt_mesh = txt_mesh.apply_transform(
        trimesh.transformations.scale_and_translate(
            scale=[1, 1, 1],
            translate=[length / 2, diameter / 2 - 0.5 * thickness, height / 2],
        )
    )
    txt_mesh = wrap_around(txt_mesh)

    if brand:
        # Generate brand mesh
        brand_width = 30
        brand_tag = tag(
            "Tetsudau",
            os.path.join(font_dir, "Allison", "Allison-Regular.ttf"),
            brand_width,
            height,
            shape=None,
            outline=False,
        )
        brand_tag.generate_svg_file(os.path.join(output_path, "brand.svg"))
        brand_mesh = mesh_from_path(os.path.join(output_path, "brand.svg"), -thickness)
        brand_mesh = brand_mesh.apply_transform(
            trimesh.transformations.rotation_matrix(angle=-np.pi / 2, direction=[1, 0, 0])
        )
        brand_mesh = brand_mesh.apply_transform(
            trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1])
        )
        brand_mesh = brand_mesh.apply_transform(
            trimesh.transformations.scale_and_translate(
                scale=[1, 1, 1],
                translate=[brand_width / 2, -diameter / 2 + 0.9 * thickness, 10],
            )
        )
        brand_mesh = wrap_around(brand_mesh)

    # Generate napkin mesh
    napkin_mesh = trimesh.boolean.difference([ring_mesh, txt_mesh])
    if brand:
        napkin_mesh = trimesh.boolean.difference([napkin_mesh, brand_mesh])

    if vis == True:
        # Create a scene for visualization
        material = trimesh.visual.material.SimpleMaterial(
            diffuse=[0.8, 0.8, 0.8], ambient=[1, 1, 1], specular=None, glossiness=1
        )  # PBRMaterial(name="PLA")
        ring_mesh.visual.material = material
        txt_mesh.visual.material = material
        brand_mesh.visual.material = material
        napkin_mesh.visual.material = material

        ring_mesh.visual.face_colors = [45, 250, 250, 255]
        txt_mesh.visual.face_colors = [255, 38, 75, 255]
        brand_mesh.visual.face_colors = [255, 38, 75, 255]
        napkin_mesh.visual.face_colors = [0, 191, 255, 255]

        scene = trimesh.Scene()
        geometries = [
            ring_mesh,
            txt_mesh,
            napkin_mesh.apply_transform(
                trimesh.transformations.scale_and_translate(
                    scale=[1, 1, 1], translate=[0, 0, 1.5 * height]
                )
            ),
        ]
        if brand:
            geometries.append(brand_mesh)

        scene.add_geometry(geometries)
        R = trimesh.transformations.concatenate_matrices(
            trimesh.transformations.rotation_matrix(
                angle=-np.pi / 3, direction=[1, 0, 0]
            ),
            trimesh.transformations.rotation_matrix(angle=np.pi, direction=[0, 0, 1]),
        )
        R[0:3, 3] = [0, 3 * diameter, 3 * height]
        scene.camera_transform = R
        scene.show(viewer="gl", flags={"wireframe": False, "axis": True})

        # Write the HTML data to a file
        export(napkin_mesh, style="html", path=output_path, name=filename)
    return napkin_mesh
