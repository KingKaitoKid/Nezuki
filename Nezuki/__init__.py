__version__ = "1.0.1"

from .Http.Http import Http
from .Bot.Bot import Bot
# from .commonLoggerSingleTon import commonLoggerSingleTon # Da rivedere la struttura nuova
# from .commonLogId import commonLogId # Da rivedere la struttura nuova
from .Database.Database import Database
# from .Documentor.Documentor import Documentor # Da utilizzare un modulo pip adatto già creato
from .Http.Http import Http
from .JsonManager.JsonManager import JsonManager
# from .LogContext.LogContext import LogContext # Da rivedere la struttura nuova
# from .Logger.Logger import Logger # Da rivedere la struttura nuova
# from .Mail.Mail import Mail # Fa parte del potenziamento del rilascio potenziamento moduli
# from .PassKey import PassKey # Rimuovere perché progetto abbandonato
# from .PyModules.PyModules import PyModules # Da rimuovere perché abbandonato
# from .QrCode.QrCode import QrCode # Da aggiornare al momento corretto
# from .ServerUtils.ServerUtils import ServerUtils # Fa parte del rilascio potenziamento moduli
# from .TelegramApi.TelegramApi import TelegramApi # Appartenente al rilascio da pianificare relativo ai servizi web
# from .TelegramParser.TelegramParser import TelegramParser # Come da riga precedente
# from .Telegram.Telegram import TelegramParser_OLD # Come da riga precedente
# from .WebLogsViewer import WebLogsViewer # Come da riga precedente
from .YamlManager.YamlManager import YamlManager

__all__ = ['Bot', 'Database', 'Http', 'JsonManager', 'YamlManager']
