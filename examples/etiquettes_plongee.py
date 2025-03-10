import os
import sys

parent_dir = os.path.dirname(os.getcwd())
svg_tag_path = os.path.join(parent_dir, "svg_tag")
sys.path.append(svg_tag_path)

os.environ["path"] += r";C:\TOOLS\01_Portable\InkscapePortable\App\Inkscape\bin"
import cairosvg
from tag import tag, tag_3D, tag_3D_RV


def batch_tags(data, RV=False):
    output_path = "../examples/outputs/plongee"
    os.makedirs(output_path, exist_ok=True)

    # Génération des noms de fichiers
    tag("", os.path.join(output_path, "tag_shp.svg"), include_shape=True, outline=True)
    for item in data:
        categorie = item["Catégorie"]
        id = item["Id"]
        recto = item["Recto"]
        verso = item["Verso"]

        # Génération des noms de fichiers
        nom_fichier = f"{categorie.lower()}-{id:02d}"

        # Créer les fichiers SVG pour le recto
        output_1_r = os.path.join(output_path, nom_fichier + "_A_shp.svg")
        tag(recto, output_1_r, include_shape=True, outline=True)
        cairosvg.svg2png(
            url=output_1_r, write_to=os.path.join(output_path, nom_fichier + "_A.png")
        )
        output_2_r = os.path.join(output_path, nom_fichier + "_A_txt.svg")
        tag(recto, output_2_r, include_shape=False, outline=False)

        # Créer les fichiers SVG pour le verso
        output_1_v = os.path.join(output_path, nom_fichier + "_B_shp.svg")
        tag(verso, output_1_v, include_shape=True, outline=True)
        cairosvg.svg2png(
            url=output_1_v, write_to=os.path.join(output_path, nom_fichier + "_B.png")
        )
        output_2_v = os.path.join(output_path, nom_fichier + "_B_txt.svg")
        tag(verso, output_2_v, include_shape=False, outline=False)

        # Utilisation du verso pour générer une forme 3D si nécessaire
        input_path = output_path
        if RV == True:
            tag_3D_RV(
                nom_fichier + "_A_txt", nom_fichier + "_B_txt", input_path, output_path
            )
        else:
            tag_3D(nom_fichier + "_A_txt", input_path, output_path)
            tag_3D(nom_fichier + "_B_txt", input_path, output_path)


if __name__ == "__main__":
    import pandas as pd

    FR = [
        {"Catégorie": "Basique", "Id": 1, "Recto": "Ça va ?", "Verso": "Ok"},
        {
            "Catégorie": "Basique",
            "Id": 2,
            "Recto": "Quelle pression ?",
            "Verso": "Mi-pression Réserve",
        },
        {
            "Catégorie": "Basique",
            "Id": 3,
            "Recto": "Oreilles",
            "Verso": "Attention au milieu",
        },
        {"Catégorie": "Basique", "Id": 4, "Recto": "Attends", "Verso": "Ralentis"},
        {"Catégorie": "Sécurité", "Id": 1, "Recto": "Ça va ?", "Verso": "Ça va pas !"},
        {"Catégorie": "Sécurité", "Id": 2, "Recto": "Essoufflé", "Verso": "Panne d'air"},
        {"Catégorie": "Sécurité", "Id": 3, "Recto": "J'ai froid", "Verso": "Narcose"},
        {
            "Catégorie": "Tek",
            "Id": 1,
            "Recto": "Changement de gaz",
            "Verso": "Run-time de secours",
        },
        {"Catégorie": "Tek", "Id": 2, "Recto": "Dévidoir", "Verso": "Profondeur max ?"},
        {"Catégorie": "Autonomie", "Id": 1, "Recto": "Bateau", "Verso": "Parachute"},
        {"Catégorie": "Autonomie", "Id": 2, "Recto": "Paliers", "Verso": "Ordinateur"},
        {"Catégorie": "Autonomie", "Id": 3, "Recto": "Mètres", "Verso": "3m 6m 9m"},
        {"Catégorie": "Autonomie", "Id": 4, "Recto": "Minutes", "Verso": "1' 3' 5'"},
        {"Catégorie": "Stabilisation", "Id": 1, "Recto": "Purge", "Verso": "Gonfle"},
        {
            "Catégorie": "Stabilisation",
            "Id": 2,
            "Recto": "Stabilise-toi",
            "Verso": "Purge lente",
        },
        {
            "Catégorie": "Stabilisation",
            "Id": 3,
            "Recto": "Purge haute",
            "Verso": "Purge basse",
        },
        {"Catégorie": "Stabilisation", "Id": 4, "Recto": "Monte", "Verso": "Descends"},
        {"Catégorie": "Ventilation", "Id": 1, "Recto": "Apnée", "Verso": "Souffle"},
        {
            "Catégorie": "Ventilation",
            "Id": 2,
            "Recto": "Inspiratoire",
            "Verso": "Expiratoire",
        },
        {
            "Catégorie": "Ventilation",
            "Id": 3,
            "Recto": "Lâcher embout",
            "Verso": "Reprise embout",
        },
        {"Catégorie": "Ventilation", "Id": 4, "Recto": "Inspire", "Verso": "Expire"},
    ]

    EN = [
        {"Catégorie": "Basic", "Id": 1, "Recto": "Are you ok?", "Verso": "Ok"},
        {
            "Catégorie": "Basic",
            "Id": 2,
            "Recto": "How much air?",
            "Verso": "Half tank Low on air",
        },
        {
            "Catégorie": "Basic",
            "Id": 3,
            "Recto": "Compensate",
            "Verso": "Watch out for fauna",
        },
        {"Catégorie": "Basic", "Id": 4, "Recto": "Wait", "Verso": "Slow down"},
        {"Catégorie": "Safety", "Id": 1, "Recto": "Are you ok?", "Verso": "I'm not ok!"},
        {
            "Catégorie": "Safety",
            "Id": 2,
            "Recto": "Out of breathe",
            "Verso": "Out of air",
        },
        {"Catégorie": "Safety", "Id": 3, "Recto": "I am cold", "Verso": "Narcosis"},
        {"Catégorie": "Tek", "Id": 1, "Recto": "Change gas", "Verso": "Backup run-time"},
        {"Catégorie": "Tek", "Id": 2, "Recto": "Spool", "Verso": "Max depth?"},
        {
            "Catégorie": "Autonomy",
            "Id": 1,
            "Recto": "Boat",
            "Verso": "Surface marker buoy",
        },
        {"Catégorie": "Autonomy", "Id": 2, "Recto": "Stops", "Verso": "Computer"},
        {"Catégorie": "Autonomy", "Id": 3, "Recto": "Feet", "Verso": "10' 20' 30'"},
        {"Catégorie": "Autonomy", "Id": 4, "Recto": "Minutes", "Verso": "1' 3' 5'"},
        {"Catégorie": "Buoyancy", "Id": 1, "Recto": "Bleed the air", "Verso": "Inflate"},
        {"Catégorie": "Buoyancy", "Id": 2, "Recto": "Level off", "Verso": "Deflator"},
        {
            "Catégorie": "Buoyancy",
            "Id": 3,
            "Recto": "Higher dump valve",
            "Verso": "Lower dump valve",
        },
        {"Catégorie": "Buoyancy", "Id": 4, "Recto": "Ascend", "Verso": "Descend"},
        {
            "Catégorie": "Breathing",
            "Id": 1,
            "Recto": "Stop breathing",
            "Verso": "Breathe",
        },
        {
            "Catégorie": "Breathing",
            "Id": 2,
            "Recto": "Full lungs",
            "Verso": "Empty lungs",
        },
        {
            "Catégorie": "Breathing",
            "Id": 3,
            "Recto": "Take out regulator",
            "Verso": "Take regulator",
        },
        {
            "Catégorie": "Breathing",
            "Id": 4,
            "Recto": "Breathe-in",
            "Verso": "Breathe-out",
        },
    ]

    data = FR
    df = pd.DataFrame(data)
    print(df)

    batch_tags(data, RV=True)
