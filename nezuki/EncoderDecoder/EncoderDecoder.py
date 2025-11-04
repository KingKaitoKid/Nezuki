from . import __version__, logger

class EncoderDecoder:
    """Classe base per gestire encoding, decoding, hashing e crittografia."""
    
    __version__ = __version__
    
    def __init__(self):
        pass

    def encode(self, data: str) -> str:
        """Metodo generico per la codifica. Da implementare nelle sottoclassi."""
        logger.error("Metodo encode() non implementato.", extra={'internal': True})
        raise NotImplementedError("Il metodo encode() deve essere implementato nelle sottoclassi.")

    def decode(self, encoded_data: str) -> str:
        """Metodo generico per la decodifica. Da implementare nelle sottoclassi."""
        logger.error("Metodo decode() non implementato.", extra={'internal': True})
        raise NotImplementedError("Il metodo decode() deve essere implementato nelle sottoclassi.")