from setuptools import setup, find_packages
from pathlib import Path

# 📜 Legge la descrizione lunga dal README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='nezuki',  # Nome in minuscolo
    version='2.0.2',
    author='Sergio Catacci',
    author_email='sergio.catacci@icloud.com',
    description='Un pacchetto per la gestione della domotica e servizi server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/KingKaitoKid/Nezuki',
    packages=find_packages(include=["nezuki", "nezuki.*"]),  # Cerca automaticamente i pacchetti in "nezuki/"
    package_dir={"": "."},  # Indica che i moduli sono in "nezuki/"
    include_package_data=True,  # Includi eventuali file extra (da MANIFEST.in)
    install_requires=[
        'cloudflare', 'colorama', 'Flask', 'Flask_Cors', 
        'jsonpath_ng', 'PyYAML', 'requests', 'mysql-connector-python'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    keywords='nezuki domotica home-server',
    project_urls={
        'Bug Reports': 'https://github.com/KingKaitoKid/Nezuki/issues',
        'Source': 'https://github.com/KingKaitoKid/Nezuki',
    },
)