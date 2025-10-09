from . import __version__, logger
import pdfplumber, typing, json, base64, io
from datetime import datetime
from pydantic import BaseModel
from nezuki.JsonManager import JsonManager

class Anagrafica(BaseModel):
    ragione_sociale: str
    livello: str
    qualifica: str
    matricola: str
    codice_fiscale: str

class Azienda(BaseModel):
    nome: str
    indirizzo: str
    provincia: str
    provincia_iso: str

class Cedolini(BaseModel):
    mese: str
    anno: str
    scatto_anzianita: str
    data_assunzione: str

class Busta(BaseModel):
    netto: float
    lordo: float
    trattenute: float

class TFR(BaseModel):
    totale: float
    mese: float

class Ferie(BaseModel):
    godute: float
    residue: float
    maturate: float

class Permessi(BaseModel):
    goduti: float
    residui: float
    maturati: float

class BustaPaga(BaseModel):
    anagrafica: Anagrafica
    azienda: Azienda
    cedolino: Cedolini
    busta: Busta
    tfr: TFR
    ferie: Ferie
    permessi: Permessi

class BustaPagaAppleNumbers(BaseModel):
    meseCedolino: str
    totaleLordo: float
    totaleTFR: float
    ferieResidue: float
    azienda: str
    dataAssunzione: str
    totaleNetto: float
    permessoResiduo: float
    ferieGodute: float
    indirizzoSede: str
    permessoMaturato: float
    provinciaSede: str
    permessoGoduto: float
    livelloDipendente: str
    ferieMaturate: float
    scattoAnzianita: str

class Cedolini:
    """Classe per l'analisi dei cedolini PDF."""
    
    __version__ = __version__

    def __init__(self):
        pass

    def __normalizza_data__(self, testo: str) -> str:
        if testo is not None:
            testo = testo.strip()
            try:
                # caso completo: 01/07/2024
                dt = datetime.strptime(testo, "%d/%m/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

            try:
                # caso ridotto: 5/2026
                dt = datetime.strptime(testo, "%m/%Y")
                # qui di default mettiamo giorno = 01
                return dt.strftime("%Y-%m-01")
            except ValueError:
                pass

            # se non riconosciuto, restituisco il testo originale
            return testo
        else:
            return None

    def __estrai_word__(self, page, x0, x1, top, bottom, tol=5, multi=False, join_with=" ", to_format=float):
        """
            Estrae TUTTE le parole dentro la box (con tolleranza) e le concatena.
        """
        bbox = (x0 - tol, top - tol, x1 + tol, bottom + tol)
        words = page.extract_words()

        candidati = []
        for w in words:
            if (bbox[0] <= float(w["x0"]) <= bbox[2] and
                bbox[1] <= float(w["top"]) <= bbox[3]):
                candidati.append(w)

        if not candidati:
            if to_format == float:
                return 0.0
            return None

        if multi:
            # ordina per posizione orizzontale e concatena
            candidati = sorted(candidati, key=lambda w: w["x0"])
            testo = join_with.join(w["text"] for w in candidati).strip()
        else:
            # singola parola più vicina al centro verticale
            centro_y = (top + bottom) / 2
            best = min(candidati, key=lambda w: abs(float(w["top"]) - centro_y))
            testo = best["text"]

        if to_format == float:
            # rimuovi eventuali punti e virgola
            testo = testo.replace(".", "").replace(",", ".")
            try:
                return float(testo)
            except ValueError:
                return 0.0
            
        if testo is not None:
            return testo.strip()
        else:
            if to_format == float:
                return 0.0
            return None

    def __format_numbers__(self, cedolino_parsed: dict) -> BustaPagaAppleNumbers:
        """
            Formatta i campi data in modo che siano compatibili con le scorciatoie di Apple.
            In particolare, converte le date nel formato ISO 8601 (YYYY-MM-DD).
        """
        payload = JsonManager(cedolino_parsed)
        json_response = {
            "meseCedolino": payload.retrieveKey("$.cedolino.mese") + " " + payload.retrieveKey("$.cedolino.anno"),
            "totaleLordo": payload.retrieveKey("$.busta.lordo"),
            "totaleTFR": payload.retrieveKey("$.tfr.totale"),
            "ferieResidue": payload.retrieveKey("$.ferie.residue"),
            "azienda": payload.retrieveKey("$.azienda.nome"),
            "dataAssunzione": payload.retrieveKey("$.cedolino.data_assunzione"),
            "totaleNetto": payload.retrieveKey("$.busta.netto"),
            "permessoResiduo": payload.retrieveKey("$.permessi.residui"),
            "ferieGodute": payload.retrieveKey("$.ferie.godute"),
            "indirizzoSede": payload.retrieveKey("$.azienda.indirizzo"),
            "permessoMaturato": payload.retrieveKey("$.permessi.maturati"),
            "provinciaSede": payload.retrieveKey("$.azienda.provincia"),
            "permessoGoduto": payload.retrieveKey("$.permessi.goduti"),
            "livelloDipendente": payload.retrieveKey("$.anagrafica.livello"),
            "ferieMaturate": payload.retrieveKey("$.ferie.maturate"),
            "scattoAnzianita": payload.retrieveKey("$.cedolino.scatto_anzianita")
        }
        return json_response

    def analizza_cedolino(self, pdf: str, page_number: int = 0, format: typing.Literal["dict", "json"] = "dict", output: typing.Literal["dict", "numbers"] = "dict")-> dict|str:
        """
            Estrae i dati principali dal cedolino PDF specificato.
            Estrae e restituisce un dizionario strutturato con i seguenti campi:
            - anagrafica: dati personali del dipendente
            - azienda: dati dell'azienda
            - cedolino: informazioni sul cedolino (mese, anno, scatto anzianità, data assunzione)
            - busta: importi netti, lordi e trattenute
            - tfr: totale e valore mensile del TFR
            - ferie: ferie godute, residue e maturate
            - permessi: permessi goduti, residui e maturati
            Il risultato è un dizionario pronto per essere convertito in un modello Pydantic.

            Args:
                pdf (str|bytes, obbligatorio):
                    Percorso del file PDF, stringa base64 o bytes
                page_number (int, facoltativo):
                    Numero della pagina da analizzare. Defaults to 0.
                format (Literal["dict", "json"], facoltativo):
                    Indica il formato di dato da restituire. Defaults to "dict".
                output (["dict", "numbers"], facoltativo):
                    Specifica il formato di output desiderato. Defaults to "dict".

            Returns:
                dict|str: Dati estratti dal cedolino nel formato specificato.

            Raises:
                ValueError: Se il formato della sorgente non è supportato.
            """

        pdf_file = None
        if isinstance(pdf, str):
            if pdf.strip().endswith(".pdf"):
                logger.debug(f"Caricamento PDF da file: {pdf}", extra={"internal": True})
                pdf_file = pdf
            else:
                # trattiamo come base64
                logger.debug("Caricamento PDF da stringa base64", extra={"internal": True})
                pdf_bytes = base64.b64decode(pdf)
                pdf_file = io.BytesIO(pdf_bytes)
        elif isinstance(pdf, (bytes, bytearray)):
            logger.debug("Caricamento PDF da bytes", extra={"internal": True})
            pdf_file = io.BytesIO(pdf)
        else:
            logger.error("Formato sorgente non supportato", extra={"internal": True})
            raise ValueError("Formato sorgente non supportato")


        with pdfplumber.open(pdf_file) as pdf:
            page = pdf.pages[page_number]
            

            json_busta = {
                "anagrafica": {
                    "ragione_sociale": self.__estrai_word__(page, x0=337.00, x1=400.00, top=109.00, bottom=118.00, tol=10, multi=True, to_format=str),
                    "livello": self.__estrai_word__(page, x0=276.00, x1=287.00, top=157.00, bottom=166.00, tol=10, to_format=str),
                    "qualifica": self.__estrai_word__(page, x0=121.00, x1=160.00, top=157.00, bottom=166.00, tol=10, to_format=str),
                    "matricola": self.__estrai_word__(page, x0=172.00, x1=222.00, top=109.00, bottom=118.00, tol=0, to_format=str),
                    "codice_fiscale": self.__estrai_word__(page, x0=26.00, x1=117.00, top=133.00, bottom=142.00, tol=10, to_format=str),
                },
                "azienda": {
                    "nome": self.__estrai_word__(page, x0=49.00, x1=200.00, top=31.00, bottom=40.00, tol=0, multi=True, to_format=str),
                    "indirizzo": self.__estrai_word__(page, x0=49.00, x1=152.00, top=40.00, bottom=49.00, tol=0, multi=True, to_format=str),
                    "provincia": self.__estrai_word__(page, x0=49.00, x1=76.00, top=50.00, bottom=59.00, tol=0, to_format=str),
                    "provincia_iso": self.__estrai_word__(page, x0=84.00, x1=98.00, top=50.00, bottom=59.00, tol=0, to_format=str),
                },
                "cedolino": {
                    "mese": self.__estrai_word__(page, x0=26.29, x1=67.81, top=109.23, bottom=118.29, tol=10, to_format=str),
                    "anno": self.__estrai_word__(page, x0=70.30, x1=90.32, top=109.29, bottom=118.29, tol=10, to_format=str),
                    "scatto_anzianita": self.__normalizza_data__(self.__estrai_word__(page, x0=465.00, x1=493.00, top=133.00, bottom=142.00, tol=10, to_format=str)),
                    "data_assunzione": self.__normalizza_data__(self.__estrai_word__(page, x0=520.00, x1=565.00, top=109.00, bottom=118.00, tol=10, to_format=str)),
                },
                "busta": {
                    "netto": self.__estrai_word__(page, x0=535.83, x1=570.86, top=612.72, bottom=621.72, tol=10),
                    "lordo": self.__estrai_word__(page, x0=70.00, x1=105.00, top=493.00, bottom=502.00, tol=10),
                    "trattenute": self.__estrai_word__(page, x0=543.00, x1=570.00, top=565.00, bottom=574.00, tol=10),
                },
                "tfr": {
                    "totale": self.__estrai_word__(page, x0=536.4, x1=571.42, top=685.29, bottom=694.29, tol=10),
                    "mese": float(self.__estrai_word__(page, x0=317.00, x1=345.00, top=685.00, bottom=694.00, tol=10) or 0)

                },
                "ferie": {
                    "godute": self.__estrai_word__(page, x0=144.00, x1=161.00, top=636.00, bottom=645.00, tol=10, to_format=float),
                    "residue": self.__estrai_word__(page, x0=189.00, x1=206.00, top=636.00, bottom=645.00, tol=10, to_format=float),
                    "maturate": self.__estrai_word__(page, x0=94.00, x1=117.00, top=636.00, bottom=645.00, tol=10, to_format=float),
                },
                "permessi": {
                    "goduti": self.__estrai_word__(page, x0=320.00, x1=342.00, top=636.00, bottom=645.00, tol=10, to_format=float),
                    "residui": self.__estrai_word__(page, x0=364.00, x1=387.00, top=636.00, bottom=645.00, tol=10, to_format=float),
                    "maturati": self.__estrai_word__(page, x0=275.00, x1=298.00, top=636.00, bottom=645.00, tol=10, to_format=float),
                },
            }
        
        if output == "dict":
            cedolino_format = json_busta
        elif output == "numbers":
            cedolino_format = self.__format_numbers__(json_busta)
        else:
            cedolino_format = json_busta

        if format == "dict":
            logger.debug(f"Cedolino dict: {cedolino_format}", extra={"internal": True})
            return cedolino_format
        elif format == "json":
            logger.debug(f"Cedolino json: {cedolino_format}", extra={"internal": True})
            return json.dumps(cedolino_format)