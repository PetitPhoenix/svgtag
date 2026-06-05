# Changelog

Toutes les modifications notables de svgtag.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
versionnage [SemVer](https://semver.org/lang/fr/).

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
