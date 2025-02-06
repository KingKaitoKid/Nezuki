import json
from Common import *
from commonLogId import *

@versione("1.0.6")
@deprecated("1.0.10", "Modulo in dismissione, usare ServerUtils")
class File:
    """ Classe che permette di leggere file, file di property e JSON """

    path: str
    """ Path assoluto della cartella dalla quale si vogliono leggere file """

    config:dict
    """ JSON di configurazioni desiderata, letta dal file properties.json """

    
    def __init__(self, base_path: str) -> None:
        """ Inizializza l'oggetto File """
        self.logger = get_logger()

        if base_path.endswith("/"):
            self.path = base_path
        else:
            self.path = base_path + "/"

    def load_property(self, typeProperty:str, env: str)->None:
        """ Legge le properties e salva quella desiderata dentro config """
        try:
            self.config = {"ok": True, "property": self.read_json("properties.json")[typeProperty][env], "error": None}
            self.logger.info(f"Property {typeProperty} per l'env {env} caricata con successo", extra={"internal": True, "esito_funzionale": 0, "details": f"{self.config}"})
        except KeyError as KeyNotFound:
            self.config = {"ok": False, "property": None,  "error": f"Chiave {typeProperty} non trovata nelle property"}
            self.logger.error(f"Non è stata trovata la property {typeProperty} per l'env {env}", extra={"internal": True, "esito_funzionale": 1, "details": f"{self.config}"})
        except Exception as e:
            self.config = {"ok": False, "property": None,  "error": "Errore generico"}
            self.logger.critical(f"Si è verificato un errore imprevisto", extra={"internal": True, "esito_funzionale": 1, "details": f"{str(e)}"})

    @deprecated("1.0.10", "usare la funzione dal modulo JsonManager")
    def read_json(self, file_name: str) -> dict:
        """
            Legge il file indicato (senza / iniziale) e torna il contenuto del file JSON decodificato.

            Input:

                file_name: Nome del file JSON da leggere
        """
        try:
            with open("{}{}".format(self.path, file_name), "r") as file_json:
                content_json = json.loads(file_json.read())
        except Exception as e:
            content_json = None
        return content_json
    
    
    def read_file(self, file_name: str) -> str:
        """
            Legge il file indicato (senza / iniziale) e torna il contenuto del file in formato stringa

            Input:
            
                file_name: Nome del file da leggere
        """
        try:
            with open("{}{}".format(self.path, file_name), "r") as f:
                content_file = f.read()
        except Exception as e:
            content_file = None
        return content_file