import os
import shutil
import subprocess
import sys
import zipfile

from PIL import Image


def prepare_target_directory(svg_file_path, clean=True):
    if not os.path.exists(svg_file_path):
        print(f"Le fichier spécifié n'existe pas : {svg_file_path}")
        sys.exit(1)
    base_name = os.path.basename(svg_file_path)
    directory_name = base_name.replace(".svg", "")
    parent_directory = os.path.dirname(svg_file_path)
    target_directory = os.path.join(parent_directory, directory_name)

    # Vérifier si le sous-répertoire existe déjà
    if os.path.exists(target_directory):
        # Lister les fichiers dans le répertoire si ce n'est pas vide
        files = os.listdir(target_directory)
        if files:
            print(f"Le répertoire {target_directory} contient les fichiers suivants :")
            for file in files:
                print(f"- {file}")
            # Demander confirmation pour supprimer
            if clean == True:
                # Supprimer les fichiers
                for file in files:
                    file_path = os.path.join(target_directory, file)
                    os.remove(file_path)
                print("Tous les fichiers ont été supprimés.")
            else:
                print("Opération annulée. Aucun fichier n'a été supprimé.")
                sys.exit(0)
    else:
        # Créer le sous-répertoire s'il n'existe pas déjà
        os.makedirs(target_directory)

    # Déplacer le fichier SVG dans le répertoire cible et mettre à jour le chemin
    new_svg_path = os.path.join(target_directory, base_name)
    shutil.move(svg_file_path, new_svg_path)
    print(f"Fichier SVG déplacé : {svg_file_path} -> {new_svg_path}")

    # Retourner le nouveau chemin du fichier SVG et le répertoire cible
    return new_svg_path


def zip_subdirectory(directory, clean=False):
    zip_path = os.path.join(
        os.path.dirname(directory), f"{os.path.basename(directory)}.zip"
    )
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Parcourir récursivement tous les fichiers dans le sous-répertoire
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                # Ajouter chaque fichier au ZIP, en spécifiant le chemin relatif
                # Cela permet de s'assurer que les fichiers sont ajoutés sans le préfixe du répertoire parent
                zipf.write(file_path, arcname=os.path.relpath(file_path, start=directory))
                print(f"Fichier ajouté au ZIP : {file_path}")
    if clean == True:
        shutil.rmtree(directory)
    print(f"Archive ZIP créée : {zip_path}")


def convert_svg_to_jpg(png_file_path):
    img = Image.open(png_file_path)
    jpg_file_path = png_file_path.replace(".png", ".jpg")
    img.convert("RGB").save(jpg_file_path, quality=95)
    print(f"Fichier JPG généré : {jpg_file_path}")


def convert_svg_with_inkscape(svg_file_path, inkscape_path, output_formats, dpi):
    if "jpg" in output_formats and "png" not in output_formats:
        output_formats.append("png")

    for fmt in output_formats:
        if fmt != "jpg":
            output_file_path = svg_file_path.replace(".svg", f".{fmt}")
            command = [
                inkscape_path,
                "--batch-process",
                "--export-filename=" + output_file_path,
                "--export-dpi=" + str(dpi),
                "--export-type=" + fmt,
                svg_file_path,
            ]
            subprocess.run(command, check=True)
            print(f"Fichier {fmt.upper()} généré : {output_file_path}")
        elif fmt == "jpg":
            png_file_path = svg_file_path.replace(".svg", ".png")
            convert_svg_to_jpg(png_file_path)


if __name__ == "__main__":
    # Remplacez ces chemins par les vôtres
    inkscape_path = "<chemin_vers_inkscape>/inkscape"
    svg_file_path = "<chemin/vers/votre/fichier.svg>"
    output_formats = ["png", "jpg", "pdf", "eps", "dxf"]
    dpi = 600
    svg_file_path = prepare_target_directory(svg_file_path, clean=True)
    convert_svg_with_inkscape(svg_file_path, inkscape_path, output_formats, dpi)

    directory = os.path.dirname(svg_file_path)
    zip_subdirectory(directory)
