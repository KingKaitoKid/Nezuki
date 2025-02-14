import smtplib, os
from email.message import EmailMessage
from File import File
from Common import *
from commonLogId import *


@versione("1.0.1")
class Mail:
    """
        questa classe permette di inviare delle email
    """

    v: str
    """ Versione modulo Mail """

    mimeTypeMail: str
    """ DEPRECATION!! Non verrà più usata in futuro. MimeType del testo della mail, di default è html"""

    env:str
    """ Identifica l'ambiente in cui viene eseguito lo script, se non passato viene prende quello della variabile d'ambiente server """

    senderName:str
    """ DEPRECATION!! Non verrà più usata in futuro. Come far visualizzare il nome de mittente, default Infrastructure """

    mailPath:str
    """ Path alla cartella di dove si trova questo script """

    def __init__(self, env:str = "", senderName:str = "Infrastruttura", mimeType:str = "html"):
        self.logger = get_logger()
        self.v = "1.0.0"
        self.env:str = env
        if self.env == "":
            self.env = os.getenv("env")
        self.mimeTypeMail:str = mimeType
        self.mailPath = os.path.dirname(__file__)
        self.load_configuration()

    def build_senderMail(self, senderName:str = "Infrastructure") -> str:
        """ Genera nel formato corretto la visualizzazione del mittente """
        return "{} <{}>".format(senderName, self.rootMail)

    def load_configuration(self):
        """ Legge le configurazioni correttamente """
        configF:File = File(self.mailPath)
        configF.load_property("SMTP", self.env)
        print("\n\n", configF.config, "\n\n")
        self.rootMail = configF.config['property']['root_email']
        self.smtphost = configF.config['property']['host']
        self.smtpport = configF.config['property']['port']
        self.user = configF.config['property']['user']
        self.passw = configF.config['property']['pass']

    def sendMail(self, nameSender:str, dest:list|str, obj:str, body:str, Cc:list|str|None=None)->None:
        """ Invia una mail ad un destinatario o più destinatari, se un destinatario inserire direttamente la mail altrimenti fare un array di stringhe di destinatari."""
        try:
            msg = EmailMessage()
            msg.set_content(body)

            msg['Subject'] = obj
            msg['From'] = self.build_senderMail(nameSender)
            if type(dest) is str:
                msg['To'] = dest
            else:
                msg['To'] = ', '.join(dest)
            
            if Cc != "" and Cc != None:
                if type(Cc) is str:
                    msg['Cc'] = Cc
                else:
                    msg['Cc'] = ', '.join(Cc)

            msg.add_alternative(body, subtype=self.mimeTypeMail)
            
            self.logger.debug(f"Email pronta all'invio", extra={"internal": True, "details": f"{msg}"})

            # Prova a inviare la mail con la gestione degli errori
            with smtplib.SMTP(self.smtphost, self.smtpport) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(self.user, self.passw)
                smtp_server.send_message(msg)

            self.logger.debug(f"Email inviata con successo", extra={"esito_funzionale": 0, "details": f"{msg}"})
        
        except smtplib.SMTPAuthenticationError as e:
            self.logger.critical(f"Errore di autenticazione SMTP", extra={
                "esito_funzionale": "SMTP Authentication Error", 
                "details": str(e)
            })
        
        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"Destinatari rifiutati", extra={
                "esito_funzionale": "SMTP Recipients Refused",
                "details": str(e)
            })
        
        except smtplib.SMTPException as e:
            self.logger.critical(f"Errore generale SMTP", extra={
                "esito_funzionale": "SMTP Error",
                "details": str(e)
            })

        except Exception as e:
            self.logger.critical(f"Errore generico durante l'invio dell'email", extra={
                "esito_funzionale": "SMTP Generic Error",
                "details": str(e)
            })

# mm = Mail("DEV")
# mm.sendMail(nameSender="Test positional sendMail", Cc=["andreacolangelo04@icloud.com"], dest=["djstrix@me.com"], obj="Test VSCode sendMail", body="Test di invio mail con array di destinatario e Cc array, test di logica")
# mm.sendMail(nameSender="Test positional sendMail", Cc="andreacolangelo04@icloud.com", dest="djstrix@me.com", obj="Test VSCode sendMail", body="Test di invio mail con stringa di destinatario e Cc stringa, test di logica")