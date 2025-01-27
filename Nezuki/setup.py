# setup.py

from setuptools import setup, find_packages
from pathlib import Path

# Legge il contenuto di README.md per la descrizione lunga
this_directory = Path(__file__).parent.parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='Nezuki',  # Nome del pacchetto
    version='0.1.0',  # Versione iniziale
    author='Sergio Catacci',  # Autore del pacchetto
    author_email='sergio.catacci@icloud.com',  # Email dell'autore
    description='Un pacchetto di moduli che implementa funzionalità relative all\'Home Server e gestione dei servizi forniti dalla Domotica. I moduli forniti anche se usati dal server della domotica possono essere utilizzati in qualsiasi ambito se il loro utilizzo rispechcia pienamente le necessità.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/KingKaitoKid/Nezuki',  # URL del repository
    packages=find_packages(),  # Trova automaticamente tutti i pacchetti e sottopacchetti
    include_package_data=True,  # Includi i file non-Python specificati in MANIFEST.in
    install_requires=['cloudflare', 'colorama', 'Flask', 'Flask_Cors', 'jsonpath_ng', 'PyYAML', 'requests', 'mysql-connector-python'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Sostituisci con la tua licenza
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    keywords='nezuki database http requests request',  # Parole chiave per la ricerca
    project_urls={
        'Bug Reports': 'https://github.com/KingKaitoKid/Nezuki/issues',
        'Source': 'https://github.com/KingKaitoKid/Nezuki',
    },
)
