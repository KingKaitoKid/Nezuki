from . import __version__
from versioning import *
from nezuki.JsonManager import JsonManager
import yaml

@deprecated("2.1.0", "Modulo dismesso per intero, usare nezuki.Parser", tipo="Modulo")
class YamlManager:
    '''
        Questa classe serve per gestire un yaml file.
    '''

    __version__ = __version__
    
    def __init__(self, yaml_file:str=None) -> None:
        """
            Inizializza il gestore YAML.
            Args:
                yaml_file (str, optional): Path del file YAML da caricare. Defaults to None [legacy].
        """
        self.data = self.read_yaml(yaml_file)
        self.dataManager = JsonManager(self.data)
    
    @legacy("2.0.0", "Funzione dismessa, usare la nuova funzione parse_yaml di nezuki.Parser modulo Yaml", "2.1.0")
    def read_yaml(self, path: str) -> dict:
        """
            Legge il file da path assoluto e torna il contenuto del file in un JSON decodificato.

            Args:
                path: Path asosluto del file YAML da leggere

            Returns:
                dict: Torna il contenuto YAML nel formato JSON
        """
        try:
            with open(path, "r") as f:
                content_json = yaml.safe_load(f.read())
        except Exception as e:
            content_json = None
        return content_json