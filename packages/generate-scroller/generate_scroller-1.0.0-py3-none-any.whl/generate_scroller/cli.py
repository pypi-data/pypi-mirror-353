import os
import sys
import time
import argparse

DEFAULT_EXCLUDED_DIRS = {
    '.git', '.vscode', '.env', 'env', '.venv', '__pycache__',
    'build', 'dist', 'media', 'static', 'downloads',
    'migrations', 'htmlcov', '.tox', '.nox', '.hypothesis',
    '.pytest_cache', '.scrapy', 'docs/_build', '.pybuilder',
    'target', '.ipynb_checkpoints', 'profile_default',
    '.mypy_cache', '__pypackages__', '.pyre', '.pytype',
    'cython_debug', '.idea', '.ropeproject', '.spyderproject',
    '.spyproject', 'instance', '.webassets-cache', 'site'
}

DEFAULT_EXCLUDED_FILES = {
    'requirements.txt', '.gitignore', 'db.sqlite3', 'db.sqlite3-journal',
    'local_settings.py', 'setup.cfg', 'dump.rdb', 'celerybeat-schedule.db',
    'celerybeat-schedule', 'celerybeat.pid', 'pip-log.txt',
    'pip-delete-this-directory.txt', '.python-version',
    'Pipfile.lock', 'poetry.lock', 'pdm.lock', '.pdm.toml',
    'MANIFEST'
}

DEFAULT_EXCLUDED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
    '.svg', '.webp', '.ttf', '.otf', '.woff', '.woff2',
    '.eot', '.css', '.js', '.ts', '.html', '.htm',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.exe',
    '.dll', '.bin', '.zip', '.tar', '.gz', '.rar', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.pyc', '.class', '.so', '.dylib', '.log', '.cover', '.mo', '.pot',
    '.manifest', '.spec', '.coverage', '.sage.py',
    '.dmypy.json', 'dmypy.json', '.py,cover'
}


def collect_files(root_dir, excluded_dirs, excluded_files, excluded_exts, included_exts=None):
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if file in excluded_files or ext in excluded_exts:
                continue
            if included_exts and ext not in included_exts:
                continue
            file_paths.append(os.path.join(root, file))
    return file_paths


def display_progress(current, total, current_file):
    bar_length = 50
    progress = current / total
    filled_len = int(bar_length * progress)
    bar = '█' * filled_len + '-' * (bar_length - filled_len)
    percent = round(progress * 100, 2)
    sys.stdout.write(f'\r[{bar}] {percent}% - {os.path.relpath(current_file)}')
    sys.stdout.flush()


def write_to_scroller(file_paths, output_file):
    total_files = len(file_paths)
    with open(output_file, 'w', encoding='utf-8') as out:
        for i, path in enumerate(file_paths, 1):
            display_progress(i, total_files, path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"<Error reading file: {e}>"
            out.write(f"# {os.path.relpath(path)}\n")
            out.write(content + "\n\n")
            time.sleep(0.01)
    print(f"\n\n✅ Terminé. Fichier généré : '{output_file}'.")


def main():
    parser = argparse.ArgumentParser(description="Créer un fichier scroller.md avec les chemins et contenus des fichiers.")
    parser.add_argument('--dir', type=str, default=os.getcwd(), help="Répertoire à scanner (par défaut: répertoire courant)")
    parser.add_argument('--output', type=str, default='scroller.md', help="Nom du fichier de sortie")
    parser.add_argument('--include-ext', type=str, help="Extensions de fichier à inclure (ex: .py,.md)")
    parser.add_argument('--exclude-ext', type=str, help="Extensions supplémentaires à exclure (ex: .log,.tmp)")

    args = parser.parse_args()

    included_exts = set(ext.strip().lower() for ext in args.include_ext.split(',')) if args.include_ext else None
    excluded_exts = DEFAULT_EXCLUDED_EXTENSIONS.copy()
    if args.exclude_ext:
        excluded_exts.update(ext.strip().lower() for ext in args.exclude_ext.split(','))

    print(f"\n📁 Répertoire analysé : {args.dir}")
    if included_exts:
        print(f"✅ Filtres appliqués : uniquement {included_exts}")
    else:
        print(f"❌ Extensions exclues : {excluded_exts}")

    file_list = collect_files(args.dir, DEFAULT_EXCLUDED_DIRS, DEFAULT_EXCLUDED_FILES, excluded_exts, included_exts)

    if not file_list:
        print("⚠️ Aucun fichier correspondant trouvé.")
        return

    write_to_scroller(file_list, args.output)


def run():
    main()
