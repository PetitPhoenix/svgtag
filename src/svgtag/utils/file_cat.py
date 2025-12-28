import os


def concatener_contenus(repertoire, fichier_sortie):
    with open(fichier_sortie, "w", encoding="utf-8") as sortie:
        for racine, dossiers, fichiers in os.walk(repertoire):
            # Exclure les dossiers __pycache__
            dossiers[:] = [d for d in dossiers if d != "__pycache__"]
            for nom_fichier in fichiers:
                chemin_complet = os.path.join(racine, nom_fichier)
                # Écrire le chemin du fichier dans le fichier de sortie
                sortie.write(chemin_complet + "\n\n")

                # Lire et écrire le contenu du fichier
                try:
                    with open(chemin_complet, encoding="utf-8") as fichier:
                        contenu = fichier.read()
                        sortie.write(contenu)
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {chemin_complet}: {e}")

                # Écrire la ligne de séparation
                sortie.write("\n\n" + "-" * 6 + "\n\n")


repertoire_a_parcourir = r"C:\TOOLS\Perso\SVGtag\tests"
fichier_de_sortie = r"C:\TOOLS\Perso\SVGtag\draft\0_cat_tests.txt"
concatener_contenus(repertoire_a_parcourir, fichier_de_sortie)
