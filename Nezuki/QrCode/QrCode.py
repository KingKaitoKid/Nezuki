import qrcode, base64
from io import BytesIO
from commonLogId import *
from Common import *
from GeneratoreCodici import GeneratoreCodici

@versione("1.0.0")
class QrCode(GeneratoreCodici):
    """ Crea un qrcode """

    data: str
    """La stringa che ti genera il qr code una volta scansionato"""

    formato: str
    """Formato della foto risultate
         Default: PNG
    """
    
    versione: int
    """Versione del qr code
        Default: 2
    """

    boxSide: int
    """Grandezza del immagine
        Default: 10
    """
    
    border: int
    """Grandezza del padding interno
        Default: 4
    """

    def __init__(self) -> None:
        """ Inizializza l'oggetto QrCode """

        super().__init__()
        self.logger = get_logger()

    def crea(self, data:str, formato:str="PNG", versione:int=2, boxSide:int=10, border:int=4):
        """ Crea l'immagine del Qr code """

        self.data = data
        self.formato = formato
        self.versione = versione
        self.boxSide = boxSide
        self.border = border

        qr = qrcode.QRCode(
            version=self.versione,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.boxSide,
            border=self.border,
        )
        qr.add_data(self.data)
        qr.make(fit=True)
        # Genera l'immagine QR code
        img = qr.make_image(fill="black", back_color="white")

        # Salva l'immagine in memoria come PNG
        buffered = BytesIO()
        img.save(buffered, format=self.formato)

        codice = base64.b64encode(buffered.getvalue()).decode('utf-8')

        self.logger.debug("Qr Code generato", extra={'details': f"qrCode: {codice}\n", 'internal': True})
        # Ottieni i byte dell'immagine e codificali in base64
        return codice