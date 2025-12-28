#!/usr/bin/env python3
"""
tree.py — affiche l'arborescence d'un dossier, en excluant .venv, __pycache__, .git.

Usage:
  python tree.py
  python tree.py C:\TOOLS\perso\svgtag
  python tree.py . -L 4

Options:
  -L, --max-depth N   limite la profondeur (par défaut: illimité)
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, Set


DEFAULT_EXCLUDES: Set[str] = {".venv", "__pycache__", ".git"}


def iter_children(path: Path, excludes: Set[str]) -> list[Path]:
    try:
        items = list(path.iterdir())
    except (PermissionError, FileNotFoundError):
        return []
    # Exclure par nom de dossier/fichier
    items = [p for p in items if p.name not in excludes]
    # Trier: dossiers d'abord, puis fichiers, puis alpha
    items.sort(key=lambda p: (p.is_file(), p.name.lower()))
    return items


def print_tree(root: Path, excludes: Set[str], max_depth: int | None) -> None:
    root = root.resolve()
    print(str(root))

    def walk(dir_path: Path, prefix: str, depth: int) -> None:
        if max_depth is not None and depth > max_depth:
            return

        children = iter_children(dir_path, excludes)
        n = len(children)

        for i, child in enumerate(children):
            is_last = (i == n - 1)
            branch = "└── " if is_last else "├── "
            print(prefix + branch + child.name)

            if child.is_dir():
                extension = "    " if is_last else "│   "
                walk(child, prefix + extension, depth + 1)

    walk(root, "", 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Afficher un tree avec exclusions.")
    parser.add_argument("path", nargs="?", default=".", help="Dossier racine (défaut: .)")
    parser.add_argument("-L", "--max-depth", type=int, default=None, help="Profondeur max (défaut: illimité)")
    args = parser.parse_args()

    print_tree(Path(args.path), DEFAULT_EXCLUDES, args.max_depth)


if __name__ == "__main__":
    main()
