__version__ = "1.0.1"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

from .EncoderDecoder import EncoderDecoder
from .qrCode import QRCodeHandler as QRCode
from .hashGenerator import HashGenerator as Hash
from .aesManager import CipherHandler as AES

__all__ = ["EncoderDecoder", "QRCode", "Hash", "AES"]