from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os
from threading import local
import uuid
# from Common import versione, deprecated, compare_versions


current_version = "1.0.0"

class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', log_instance=None):
        super().__init__(fmt, datefmt, style)
        self.log_instance = log_instance

    def format(self, record):
        # Aggiunge logId al record dinamicamente
        record.logId = self.log_instance.logId
        record.msg = record.msg.replace('\n', '<br>')
        return super().format(record)

# @versione("1.0.0")
class Logger:
    """ Definisce strutture di log in modo formale e da poter essere visualizzato correttamente nel webserver """

    isLocal: bool
    """ Indica se il bot è in esecuzione in localhost o sul server """

    pathLogs: str
    """ Indica il path di dove sono salvati i log del bot """

    logId: str
    """ Identificati olog che è un UUID """

    ownerModuleLog: bool
    """ Indica l'owner del log se è Custom (sviluppatore) o Internal (log generati dalle dipendenze)"""

    def __init__(self, localMode: bool = False, localFileLogPath: str = "/", logId="First init", ownerModuleLog: bool = False):
        """ Inizializza la classe, il parametro commonLogger serve alla classe Common per loggare eventuali errori generici che si con verificati """
        self.isLocal = localMode
        self.pathLogs = localFileLogPath
        self.logId = self._update_log_id()
        self.setup_logging()
        self.ownerModuleLog:bool = ownerModuleLog
    
    def setModuleLog(self, moduleLog: bool = True):
        """ Imposta la variabile che indica se un log è interno oppure no """
        self.ownerModuleLog = moduleLog
        self.pathLogs = self.pathLogs + "/Module"

    def _update_log_id(self):
        """ Aggiorna il log id """
        self.logId = uuid.uuid1()
        return self.logId

    def setup_logging(self):
        """ Scrive i log sul terminale e file dedicato, creando il file di log della giornata, in base al peso (100MB max), conservando fino a 5 backup da 100MB (i più vecchi verranno eliminati) o gli ultimi 30 giorni"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)  # Configura il livello di log
        # Handlers per la rotazione dei log
        timed_handler = TimedRotatingFileHandler(f"{self.pathLogs}/bot_log_timed.log", when="D", interval=1, backupCount=30)
        size_handler = RotatingFileHandler(f"{self.pathLogs}/bot_log_size.log", maxBytes=200*1024*1024, backupCount=5)

        # Formatter
        if self.isLocal:
            if self.ownerModuleLog == False:
                formatter = CustomFormatter('%(asctime)s - %(levelname)s - Local - Custom - %(name)s - %(module)s - %(funcName)s - %(logId)s - %(message)s', log_instance=self)
            else:
                formatter = CustomFormatter('%(asctime)s - %(levelname)s - Local - Internal - %(name)s - %(module)s - %(funcName)s - %(logId)s - %(message)s', log_instance=self)
        else:
            if self.ownerModuleLog == False:
                formatter = CustomFormatter('%(asctime)s - %(levelname)s - Server - Custom - %(name)s - %(module)s - %(funcName)s - %(logId)s - %(message)s', log_instance=self)
            else:
                formatter = CustomFormatter('%(asctime)s - %(levelname)s - Server - Internal - %(name)s - %(module)s - %(funcName)s - %(logId)s - %(message)s', log_instance=self)
        timed_handler.setFormatter(formatter)
        size_handler.setFormatter(formatter)

        # StreamHandler per loggare anche su console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Aggiungi handlers al logger
        self.logger.addHandler(timed_handler)
        self.logger.addHandler(size_handler)
        self.logger.addHandler(console_handler)

    def get_logs(self, query=''):
        """ Ritorna i file di log dei file backup """
        log_files = [f for f in os.listdir(self.pathLogs) if (f.endswith('.log') and "bot_log_size" in f)]
        logs = []
        for log_file in log_files:
            with open(os.path.join(self.pathLogs, log_file), 'r') as f:
                for line in f:
                    if query.lower() in line.lower():
                        logs.append(line.strip())
        
        # Ordina i log in ordine decrescente per data e ora
        logs.sort(key=lambda x: datetime.strptime(x.split(" - ")[0], '%Y-%m-%d %H:%M:%S,%f'), reverse=True)
        return logs