````markdown
# generate-scroller

[![PyPI version](https://img.shields.io/pypi/v/generate-scroller.svg)](https://pypi.org/project/generate-scroller)  
[![Python Versions](https://img.shields.io/pypi/pyversions/generate-scroller.svg)](https://pypi.org/project/generate-scroller)  
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## Description

**generate-scroller** est un outil en ligne de commande pour générer un fichier Markdown (`scroller.md`) contenant les chemins et contenus des fichiers texte d’un répertoire donné.  
Il permet d’exclure automatiquement les fichiers, dossiers et extensions non pertinents, pour fournir une vue d’ensemble claire et exploitable du projet.

---

## Fonctionnalités

- Analyse récursive des dossiers
- Exclusions par défaut adaptées aux projets Python
- Filtrage fin des extensions à inclure ou exclure
- Affichage d’une barre de progression en temps réel
- Gestion robuste des erreurs de lecture
- Sortie Markdown avec titres pour chaque fichier

---

## Installation

Vous pouvez installer `generate-scroller` directement depuis PyPI :

```bash
pip install generate-scroller
````

---

## Utilisation

```bash
generate_scroller --dir chemin/vers/le/projet --output scroller.md [options]
```

### Options disponibles

* `--dir` : Répertoire à analyser (par défaut, le répertoire courant)
* `--output` : Nom du fichier de sortie Markdown (par défaut `scroller.md`)
* `--include-ext` : Extensions à inclure (exemple : `.py,.md`)
* `--exclude-ext` : Extensions supplémentaires à exclure (exemple : `.log,.tmp`)

---

## Exclusions par défaut

### Dossiers exclus

```
.git, .vscode, .env, env, .venv, __pycache__, build, dist, media, static, downloads,
migrations, htmlcov, .tox, .nox, .hypothesis, .pytest_cache, .scrapy, docs/_build,
.pybuilder, target, .ipynb_checkpoints, profile_default, .mypy_cache, __pypackages__,
.pyre, .pytype, cython_debug, .idea, .ropeproject, .spyderproject, .spyproject,
instance, .webassets-cache, site
```

### Fichiers exclus

```
requirements.txt, .gitignore, db.sqlite3, db.sqlite3-journal, local_settings.py, setup.cfg,
dump.rdb, celerybeat-schedule.db, celerybeat-schedule, celerybeat.pid, pip-log.txt,
pip-delete-this-directory.txt, .python-version, Pipfile.lock, poetry.lock, pdm.lock,
.pdm.toml, MANIFEST
```

### Extensions de fichiers exclues

```
.png, .jpg, .jpeg, .gif, .bmp, .ico, .svg, .webp,
.ttf, .otf, .woff, .woff2, .eot,
.css, .js, .ts, .html, .htm,
.mp3, .mp4, .avi, .mov, .mkv,
.exe, .dll, .bin,
.zip, .tar, .gz, .rar, .7z,
.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx,
.pyc, .class, .so, .dylib,
.log, .cover,
.mo, .pot, .manifest, .spec, .coverage,
.sage.py, .dmypy.json, dmypy.json,
.py,cover
```

---

## Contribution

Contributions, suggestions et rapports de bugs sont les bienvenus.
Merci de forker le projet et de créer une pull request.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

## Auteur

Daniel Guedegbe — [danielguedebe10027@gmail.com](mailto:danielguedebe10027@gmail.com)

---

## Project URLs

* GitHub: [https://github.com/daniel10027/generate-scroller](https://github.com/daniel10027/generate-scroller)
* PyPI: [https://pypi.org/project/generate-scroller](https://pypi.org/project/generate-scroller)

```