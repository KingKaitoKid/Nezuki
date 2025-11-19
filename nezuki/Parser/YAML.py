from . import __version__, logger
from versioning import *
from nezuki.JsonManager import JsonManager
import yaml, os, base64

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

    @legacy("2.0.0", "Funzione dismessa, usare la nuova funzione parse_yaml di nezuki.Parser modulo Yaml", "2.1.5")
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

    def _is_base64(self, s: str) -> bool:
        """Controlla rapidamente se la stringa sembra una base64 valida."""
        if not isinstance(s, str):
            return False
        try:
            # Evitiamo false positive: base64 deve avere lunghezza multipla di 4
            if len(s.strip()) % 4 != 0:
                return False
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False

    @experimental("2.1.0", "Modificato comportamento funzione per leggere dal file passato", "2.1.5")
    def parse_yaml(self, file: str|bytearray = None) -> dict:
        """
            Legge il file da path assoluto e torna il contenuto del file in un JSON decodificato.

            Args:
                file: Può essere un path assoluto del file YAML, una stringa base64 del contenuto YAML,
                      una stringa normale con il contenuto YAML, o un oggetto bytes/bytearray

            Returns:
                dict: Torna il contenuto YAML nel formato JSON, vuoto se non valido

            Raises:
                ValueError: Se il file non esiste o non è fornito
        """

        try:
            content = None
            if file:
                # 1️⃣ Se è un oggetto bytes, decodifichiamolo
                if isinstance(file, (bytes, bytearray)):
                    logger.debug("Rilevato input in bytes", extra={"internal": True})
                    content = file.decode("utf-8")
                elif os.path.exists(file):
                    logger.debug(f"Rilevato file YAML: {file}", extra={"internal": True})
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()
                # 2️⃣ Se è una stringa base64, decodifichiamola
                elif self._is_base64(file):
                    logger.debug("Rilevato input base64 YAML", extra={"internal": True})
                    try:
                        content = base64.b64decode(file).decode("utf-8")
                    except Exception as e:
                        logger.error(f"Errore nella decodifica base64: {e}", extra={"internal": True})
                        return {}

                # 3️⃣ Se è una stringa normale, usiamola direttamente
                else:
                    logger.debug("Rilevato YAML inline (stringa diretta)", extra={"internal": True})
                    content = file

                # Se non abbiamo contenuto valido, ritorniamo vuoto
                data = yaml.safe_load(content)
                if data is None:
                    logger.warning("YAML vuoto o non valido", extra={"internal": True})
                    return {}

                logger.info("YAML caricato correttamente", extra={"internal": True})
                return data
            else:
                logger.error("Nessun file o contenuto YAML fornito", extra={"internal": True})
                return {}

        except yaml.YAMLError as e:
            logger.error(f"Errore nel parsing YAML: {e}", extra={"internal": True})
        except Exception as e:
            logger.error(f"Errore generale durante il caricamento YAML: {e}", extra={"internal": True})
        return {}