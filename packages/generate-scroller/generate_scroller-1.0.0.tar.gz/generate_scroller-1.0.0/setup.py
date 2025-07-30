from setuptools import setup, find_packages

setup(
    name='generate_scroller',
    version='1.0.0',
    description='Génère un fichier Markdown avec le contenu la description  de fichiers texte du projet',
    author='Daniel Guedegbe',
    author_email='danielguedegbe10027@gmail.com',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'generate_scroller=generate_scroller.cli:run',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
