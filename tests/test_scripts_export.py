import os
import unittest
from PIL import Image
from SVGtag.scripts.export import prepare_target_directory, zip_subdirectory, convert_svg_to_jpg, convert_svg_with_inkscape

class TestSVGConversion(unittest.TestCase):
    def setUp(self):
        # Créer un répertoire temporaire pour les tests
        self.output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'scripts', 'export')
        os.makedirs(self.output_path, exist_ok=True)
  #         self.test_dir = tempfile.mkdtemp()
        # Créer un chemin de fichier SVG de test dans le répertoire temporaire
        self.test_svg_path = os.path.join(self.output_path, 'test.svg')
        # Écrire un contenu SVG simple dans le fichier de test
        with open(self.test_svg_path, 'w') as f:
            f.write('<svg height="100" width="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>')

        # Chemin vers l'exécutable Inkscape (remplacer par le chemin réel sur votre système)
        self.inkscape_path = 'inkscape'  # Inkscape doit être dans le PATH sur Ubuntu

#     def tearDown(self):
#         # Supprimer le répertoire de sortie après chaque test
#         shutil.rmtree(self.output_path)

    def test_01_prepare_target_directory(self):
        # Tester la préparation du répertoire cible
        new_svg_path = prepare_target_directory(self.test_svg_path, clean = True)
        self.assertTrue(os.path.exists(new_svg_path))
        self.assertTrue(os.path.exists(os.path.dirname(new_svg_path)))

    def test_02_convert_svg_to_jpg(self):
        # Créer un fichier PNG de test pour la conversion en JPG
        test_png_path = os.path.join(self.output_path, 'test.png')
        Image.new('RGB', (100, 100), color = 'red').save(test_png_path)
        # Convertir le fichier PNG en JPG
        convert_svg_to_jpg(test_png_path)
        # Vérifier si le fichier JPG a été créé
        test_jpg_path = test_png_path.replace('.png', '.jpg')
        self.assertTrue(os.path.exists(test_jpg_path))

    def test_03_convert_svg_with_inkscape(self):
        # Préparer le répertoire cible et obtenir le nouveau chemin SVG
        new_svg_path = prepare_target_directory(self.test_svg_path, clean = True)
        # Convertir le fichier SVG en différents formats
        output_formats = ['png', 'pdf']
        dpi = 300
        convert_svg_with_inkscape(new_svg_path, self.inkscape_path, output_formats, dpi)
        # Vérifier si les fichiers convertis ont été créés
        for fmt in output_formats:
            output_file_path = new_svg_path.replace('.svg', f'.{fmt}')
            self.assertTrue(os.path.exists(output_file_path))

    def test_04_zip_subdirectory(self):
        # Préparer le répertoire cible et obtenir le nouveau chemin SVG
        new_svg_path = prepare_target_directory(self.test_svg_path, clean = True)
        # Zipper le sous-répertoire
        zip_subdirectory(os.path.dirname(new_svg_path), clean = True)
        # Vérifier si le fichier ZIP a été créé
        zip_path = os.path.join(self.output_path, 'test.zip')
        self.assertTrue(os.path.exists(zip_path))
        
    def test_05_full_scope(self):
        # Préparer le répertoire cible et obtenir le nouveau chemin SVG
        new_svg_path = prepare_target_directory(self.test_svg_path, clean = True)
        output_formats = ['png', 'jpg', 'pdf', 'eps', 'dxf']
        dpi = 300
        convert_svg_with_inkscape(new_svg_path, self.inkscape_path, output_formats, dpi)
        # Vérifier si les fichiers convertis ont été créés
        for fmt in output_formats:
            output_file_path = new_svg_path.replace('.svg', f'.{fmt}')
            self.assertTrue(os.path.exists(output_file_path))
        zip_subdirectory(os.path.dirname(new_svg_path), clean=True)
        # Vérifier si le fichier ZIP a été créé
        zip_path = os.path.join(self.output_path, 'test.zip')
        self.assertTrue(os.path.exists(zip_path))

if __name__ == '__main__':
    unittest.main()