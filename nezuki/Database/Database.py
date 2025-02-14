from re import S
import typing
import mysql.connector
import psycopg2, psycopg2.extras
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()  # Usa il logger corretto

class Database:
    """
    Crea la connessione al Database e permette di eseguire qualsiasi query safe e non safe.

    Attributes:
        database (str): Nome del database a cui connettersi.
        connection: Connessione persistente al DB (istanza di mysql.connector.MySQLConnection o psycopg2 connection).
        db_type (str): Tipo di database, 'mysql' o 'postgresql'.
        auto_load (bool): Se True, la connessione viene caricata automaticamente.
        errorDBConnection (bool): Flag per indicare errori di connessione.
    """

    database: str
    """ Nome del Database al quale ci si vuole collegare"""

    connection: mysql.connector.MySQLConnection
    """ Connessione persistente al DB """

    configJSON: dict
    """ INTERNAL: Confgiruazioni di connessione al DB """
    
    def __init__(self, database: str = "monitoring", db_type: typing.Literal["mysql", "postgresql"] = "mysql") -> None:
        """ Inizializza l'oggetto Database.

        Args:
            database (str): Il nome del database (default "monitoring").
            db_type (str): Il tipo di database ("mysql" o "postgresql", default "mysql").
        """
        self.database = database
        self.db_type = db_type.lower()
        self.auto_load = False
        self.errorDBConnection = False

    def connection_params(self, host: str, user: str, password: str) -> dict:
        """
        Configura manualmente i parametri di connessione al database.

        Args:
            host (str): Indirizzo del server DB.
            user (str): Nome utente per la connessione.
            password (str): Password per la connessione.

        Returns:
            dict: I parametri di connessione impostati (potresti voler ritornare il dizionario o semplicemente aggiornare l'oggetto).
        """
        self.auto_load = False
        self.configJSONNew: dict = {
            "database": self.database,
            "host": host,
            "user": user,
            "password": password
        }
        try:
            logger.debug("Avvio la connessione al DB con i parametri", extra={"internal": True})
            self.connection = self.start_connection()
            self.errorDBConnection = False
            logger.debug("Connessione al DB avvenuta con successo", extra={"internal": True})
        except Exception as e:
            logger.error(f"Connessione al DB fallita. {e}", extra={"internal": True})
            raise e
    
    def start_connection(self):
        """
        Avvia la connessione al Database
        """
        if self.db_type == "mysql":
            return mysql.connector.connect(**self.configJSONNew)
        elif self.db_type == "postgresql":
            return psycopg2.connect(**self.configJSONNew)
        else:
            raise ValueError(f"Tipo di Database non supportato: {self.db_type}")
        
    
    def __sanitize_string__(self, text: str) -> str:
        """
        Effettua una trim del testo passato in input.
        
        Args:
            text (str): testo su cui applicare la trim
            
        Returns:
            str: La stringa con la trim dagli spazi iniziali e finali"""
        to_ret: str = text.strip()
        return to_ret
    
    
    def doQuery(self, query: str, params = None) -> dict :
        """
        Esegue una query sul database.

        Args:
            query (str): La query da eseguire. Se sono presenti parametri, utilizzare %s per placeholder.
            params: Parametri da passare alla query, nel formato `tuple` e, in caso di un solo parametro, mettere la virgola dopo il primo elemento `tuple`

        Returns:
            dict: Un dizionario con la struttura:
                  {"ok": Bool, "results": list, "rows_affected": int, "error": None|str, "lastrowid": Optional[int]}
        """
        if not self.errorDBConnection:
            query = self.__sanitize_string__(query)
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
                cursor.close()
            except Exception as e:
                cursor.close()
                ok: bool = False
                results = []
                rows = -1
                result_dict = {"ok": ok, "results": results, "rows_affected": rows, "error": str(e)}

            return result_dict
        else:
            return {"ok": False, "results": [], "rows_affected": -1, "error": "Connessione al DB fallita"}        
    
    def __del__(self) -> None:
        """ Chiude la connessione al DB se è stata inizializzata """
        if hasattr(self, "connection") and self.connection:
            self.connection.close()

# ddb = Database(database="postgres", db_type="postgresql")

# ddb.connection_params("kaito.link:25432", "kaito", "kaitokid11")
