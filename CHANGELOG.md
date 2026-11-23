# Changelog

Toutes les modifications notables de svgtag.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
versionnage [SemVer](https://semver.org/lang/fr/).

## [0.13.0]

### Fixed
- `examples/tag_3d_recto_verso.py` : `create_scene`, `export_stl`, `export_html`
  importés de `mesh.visualization`.
- `extrude_path`, `extrude_text` : les contours que trimesh ne construit pas
  (`None` dans `polygons_closed`) sont ignorés.
- `extrude_path`, `extrude_text` : les polygones qui se touchent sont fusionnés
  avant extrusion (union, fermeture de 0,01 mm).
- `extrude_path`, `extrude_text` : chaque extrusion est un volume une fois ses
  sommets arrondis en float32 ; sinon le polygone est accroché à une grille de
  0,1 µm, fermé, ouvert de 5 µm, ou écarté.

### Added
- Paramètre `tolerance` de `extrude_path` et `extrude_text` (`TOLERANCE` = 0,01 mm).

### Changed
- **Déplacements (imports à modifier)** :
  - `svg_to_path2d` : `mesh.extrusion` → `geom.converters` ;
  - `glyph_polygons` : `mesh.extrusion` → `geom.converters` ;
  - `prepare_for_trimesh_angles` : `mesh.svg_helpers` → `geom.converters` ;
  - `thicken_polygons` : `mesh.extrusion` → `geom.operations`.
- `geom.operations` : `resolve_polygons`, `merge_touching`, `polygons_of`,
  `repair_variants` (auparavant privées dans `mesh.extrusion`).
- `svgtag.mesh` exporte `extrude_text` au lieu de `svg_to_path2d`.
- `svg` n'importe plus `mesh` ; `geom` n'importe trimesh qu'à l'appel de
  `svg_to_path2d`.
- `geom.converters.to_svg` sans dimensions : viewBox calée sur les bornes de
  la géométrie ; `tag_*_svg` et `tablet_svg` l'utilisent.
- `svg_to_path2d` lit le SVG en mémoire (plus de fichier temporaire).
- `SVG.flip` et `SVG.flip_element` : matrice calculée par `SVG._flip_matrix`.
- `brand_layout` et `brand_layout_auto` : position calculée par
  `_flipped_position` et `_brand_origin`.
- `mesh.extrusion`, `mesh.assembly`, `prepare_for_trimesh_angles` : messages
  via `logging` au lieu de `print`.
- Dépendances déclarées dans `pyproject.toml` uniquement. Cœur : `fonttools`,
  `shapely`, `numpy`, `qrcode`. Extra `3d` : `trimesh[easy]>=4.11,<6`,
  `manifold3d>=3.0,<4`. `all` = `3d` + `developer`. Python ≥ 3.10.
- `geom.shapes.circle` : `buffer(quad_segs=…)` au lieu de `resolution=`.

### Removed
- `requirements.txt`, `requirements.in`.
- `svg/shapes/ring.py`, `svg/text2svg_self.py`, `utils/export.py`,
  `utils/file_cat.py`, `utils/list_files.py`, `utils/list_functions.py`,
  `utils/svgtag_functions.txt`, `svg/base.main()`.
- `tests/test_generator_wifi.py`, `tests/test_scripts_export.py`.
- `Pillow` de l'extra `developer`.
- `mesh/svg_helpers.py` (`prepare_face_A`, `prepare_face_B_extrusion`,
  `prepare_face_B_visual`, `svg_to_tempfile`, `convert_angle_for_trimesh`).
- `geom.converters.to_mesh`.
- `svg.text.flip`.

## [0.12.0] - 2026-07-01

### Added
- **`business_card_layout(width, height, padding)`** (`svg/layouts.py`) : mise en
  page paysage pour carte de visite (ex. 85×55 mm). Contrairement à
  `wifi_qr_layout` (pensé carré), le texte est réparti dans une colonne à gauche
  (`title`, `org`, `line1..3`) et le QR occupe un grand bloc centré verticalement
  à droite (`qr_code`) avec une zone de légende (`qr_caption`). Pas de zone
  `signal_icon`.
- **`text_svg(..., align="center"|"left"|"right")`** (`svg/text.py`) : alignement
  horizontal du texte dans sa zone. `center` par défaut → comportement inchangé.

### Changed
- **`qr_card_svg(..., layout=None)`** (`svg/shapes/qr.py`) : accepte un `Layout`
  déjà construit (défaut : `wifi_qr_layout`), ce qui permet des cartes non carrées.
  L'icône en haut à droite n'est dessinée que si le layout expose une zone
  `signal_icon` (les layouts sans cette zone, comme la carte de visite, l'ignorent).

## [0.11.0] - 2026-06-05

### Added
- **Layouts déclaratifs** : `Layout.from_spec(dict, …)` + `build_layout`,
  `validate_spec`, `zone_kinds` dans `svg/layout.py`. Une forme de plaque se
  décrit comme de la donnée (un `dict` : canvas + zones nommées + ratios +
  rôle de zone via `kind`) au lieu d'une fonction Python dédiée. svgtag reste
  agnostique du format (l'appelant fournit le dict, depuis YAML/JSON/Python) —
  **aucune dépendance ajoutée**.

## [0.10.0] - 2026-06-04

### Added
- Épaississement des glyphes (offsets) à l'extrusion, pour la lisibilité en
  gravure laser et impression 3D bi-couleur (`mesh/extrusion.py`, `svg/text.py`).

## [0.9.0] - 2026-06-04

### Added
- Brique QR générique *payload-agnostic* : `qr_payload_svg` / `qr_card_svg`
  (carte QR pour n'importe quel contenu), avec `wifi` refactoré par-dessus.
- Exemples `examples/qr_card.py` et `examples/qr_card_3d.py`.

### Changed
- QR codes agrandis (meilleure lisibilité au scan).

## [0.8.5] - 2026-05-07

### Fixed
- Corrections de rendu des tracés ; retour à un `add_element` simple.

## [0.8.4] - 2026-05-06

### Fixed
- Extrusion : imbrication et chevauchement des trous gérés de façon robuste
  pour des polices et sources SVG variées.

## [0.8.3] - 2026-05-06

### Fixed
- Extrusion : gestion correcte des trous pour les polices à enroulement de
  contour incohérent.

## [0.8.2] - 2026-04-29

### Added
- Support des géométries Shapely dans `base` / SVG.
- Contour (outline) sur les cartes.
- Générateur de rond de serviette (ring) avec visualisation ; visualisations
  et conventions revues.

### Fixed
- Nettoyage de la géométrie avant extrusion (évite des échecs).
- Courbes plus lisses (suppression d'une simplification) ; recalcul du viewBox.

## [0.8.1] - 2026-01-02

### Changed
- Mise à jour du QR code WiFi.

## [0.8.0] - 2025-12-29

### Added
- Brand layouts (logo/marque positionné dans une zone).
- Opérations de flip (recto/verso).
- Layout narcose (plaque de test de narcose : titre + consignes + zone numéros).
