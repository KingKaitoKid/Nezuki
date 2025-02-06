from re import S
import typing
import mysql.connector
import psycopg2, psycopg2.extras
from File import File
import os
from commonLogId import *
from Common import *
from JsonManager import JsonManager

@versione("1.1.0")
class Database:
    """ Crea la connessione al Database e permette di eseguire qualsiasi query safe e non safe """

    env: str 
    """ Ambiente di esecuzione, se vuoto verrà preso in considerazione l'env del server """

    fileConfig: File
    """ Gestore dei file e property.
     
      Vedere `.File` """

    database: str
    """ Nome del Database al quale ci si vuole collegare"""

    connection: mysql.connector.MySQLConnection
    """ Connessione persistente al DB """

    configJSON: dict
    """ INTERNAL: Confgiruazioni di connessione al DB """
    
    def __init__(self, env: str = "", database: str = "monitoring", db_type: typing.Literal["mysql", "postgresql"] = "mysql") -> None:
        """ Inizializza l'oggetto Database, se env è vuoto verrà considerato l'env definito sul server """
        self.logger = get_logger()
        if env == "":
            env = os.getenv("env")
        self.env = env
        self.database = database
        self.db_type = db_type.lower()
        self.auto_load = True
        self.errorDBConnection = False
        self.load_configuration()

    def connection_params(self, host: str, user: str, password: str) -> dict:
        """ Permette di passare manualmente la connessione al DB  """
        if self.errorDBConnection:
            self.logger.debug("Rilevato tentativo in errore di connessione mediante property, verrà usata la configurazione manuale")
        else:
            self.logger.warning("Connessione con le property è andato in OK, tale connessione verrà chiusa e aperta la nuova usando i parametri manuali.")
        self.auto_load = False
        self.configJSONNew: dict = {
            "database": self.database,
            "host": host,
            "user": user,
            "password": password
        }
        if not self.errorDBConnection:
            self.connection.close
        try:
            self.connection = self.start_connection()
            self.errorDBConnection = False
            self.logger.info(f"Connessione al DB {self.db_type} con parametri manuali riuscita correttamente")
        except Exception as e:
            self.logger.fatal("Impossibile connettersi al DB con i parametri manuali, controllare i parametri e/o connettività all'host")
            print(e)

    
    def load_configuration(self) -> None:
        """ Carica le property per poter avviare una connessione, eseguita automaticamente appena si crea l'istanza """
        
        JsonM = JsonManager({})
        self.configJSONNew: dict = JsonM.read_json(os.path.dirname(__file__) + "/properties.json")['DB'][self.env]
        self.configJSONNew['database'] = self.database
        try:
            self.connection = self.start_connection()
            self.logger.info("Connessione al DB riuscita mediante property")
            self.errorDBConnection = False
        except Exception as e:
            self.errorDBConnection = True
            self.logger.error("Connessione al DB Fallita mediante property, verificarle o passare manualmente i parametri con il metodo connection_params()")
    
    
    def start_connection(self):
        """ Avvia la connessione MySQL"""
        self.logger.debug("Inizio connessione al DB")
        if self.db_type == "mysql":
            return mysql.connector.connect(**self.configJSONNew)
        elif self.db_type == "postgresql":
            return psycopg2.connect(**self.configJSONNew)
        else:
            raise ValueError(f"Tipo di Database non supportato: {self.db_type}")
    
    def __sanitize_string__(self, text: str) -> str:
        to_ret: str = text.strip()
        return to_ret
    
    
    def doQuery(self, query: str, params = None) -> dict :
        """ Esegue la query passata in input e torna un array di risultati.

            - Input:
                - query: Query da eseguire, in caso di parametri usare %s
                - params: Se presenti passare i parametri associati a %s in ordine, se è presente solo 1 parametro nella tupla mettere la virgola finale            
            - Output: {"ok": Bool, "results": list(tuple(...)), "rows_affected": Int, "error": None|dict}
        """
        if not self.errorDBConnection:
            query = self.__sanitize_string__(query)
            self.logger.debug(f"Ricevuta istruzione di esecuzione query", extra={"details": f"query: {query}\nParams: {params}", "internal": True})
            result_dict: dict = {"ok": False, "results": [], "rows_affected": -1, "error": "Init phase..."}
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) if self.db_type == "postgresql" else self.connection.cursor(buffered=True)

            try:
                results = []
                lastrowid = None
                if "CALL" in query.upper().split(" ")[0]:
                    if self.db_type == "postgresql":
                        results = cursor.callproc(query, params)
                    else:
                        query = query.replace("CALL ", "")
                        results = cursor.callproc(query, params)
                    rows = 0
                else:

                    cursor.execute(query, params)
                    if (cursor.with_rows if self.db_type=="mysql" else cursor.description is not None) and  "SELECT" in query.upper().split(" ")[0]:
                        results = cursor.fetchall()
                    if "INSERT" in query.upper().split(" ")[0] or "UPDATE" in query.upper().split(" ")[0] or "DELETE" in query.upper().split(" ")[0]:
                        self.connection.commit()
                        lastrowid = cursor.lastrowid if self.db_type == "mysql" else cursor.lastrowid
                    rows = cursor.rowcount
                ok: bool = True
                result_dict = {"ok": ok, "results": results, "rows_affected": rows, "error": None, "lastrowid": lastrowid}
                self.logger.debug(f"Query eseguita", extra={"esito_funzionale": 0, "details": f"Output: {result_dict}", "internal": True})
                cursor.close()
            except Exception as e:
                cursor.close()
                ok: bool = False
                results = []
                rows = -1
                result_dict = {"ok": ok, "results": results, "rows_affected": rows, "error": str(e)}
                self.logger.error(f"La query è fallita", extra={"esito_funzionale": 1, "details": f"Riultato: {result_dict}", "internal": True})

            return result_dict
        else:
            self.logger.fatal("Impossibile eseguire la query perché la connessione al DB non è riuscita, verificare le property o passarli manualmente.")
            return {"ok": False, "results": [], "rows_affected": -1, "error": "Connessione al DB fallita"}        
    
    def __del__(self) -> None:
        """ Chiude la connessione al DB alla distruzione o cancellazione di questo oggetto """
        self.connection.close
        self.logger.debug(f"Terminazione connessione SQL")
        

# dd = Database("", "DEV")
# dd.test_db_connection()