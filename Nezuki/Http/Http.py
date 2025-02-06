import requests
# from Logger import Logger
from Common import *
from commonLogId import *

@versione("1.0.0")
class Http:
    # Fare una generale review di questo modulo

    
    def __init__(self):
        self.logger = get_logger()
        pass
    
    
    def __del__(self) -> None:
        pass
    
    
    def doRequest(self, host: str, endpoint: str, method: str="get", payload: dict={}, port: int=0, protocol: str="http") -> requests.Response:
        '''
            esegue una chiamata http generica in post o in get e torna la risposta
        '''
        port = ":{}".format(port) if port != 0 else ""
        # URL a cui effettuare la richiesta POST
        url = "{}://{}{}{}".format(protocol, host, port, endpoint)
        self.logger.debug(f"Chiamata API {url}", extra={'esito_funzionale':-1, "internal": True, 'details':f"{payload}"})
        # self.logger.debug(f"Eseguo chiamata:\n{method.upper()} {url} - Payload:\n{payload}")
        mapper = {
            "get": requests.get,
            "post": requests.post
        }
        try:
            # Invia la richiesta POST con i dati JSON
            response: requests.Response = mapper[method](url,json=payload)
            if response.status_code > 199 and response.status_code < 300:
                self.logger.debug(f"Risposta chiamata HTTP {url}", extra={'esito_funzionale':f"HTTP {response.status_code}", "internal": True, 'details':response.text})
            else:
                self.logger.error(f"Risposta chiamata HTTP {url}", extra={'esito_funzionale':f"HTTP {response.status_code}", "internal": True, 'details':response.text})

            # Ottieni il JSON di risposta
            return response
        except Exception as e:
            self.logger.fatal(f"Errore fatale/sconosciuto per la chiamata {url}", extra={'esito_funzionale': f"HTTP 500", "internal": True, 'details': str(e)})