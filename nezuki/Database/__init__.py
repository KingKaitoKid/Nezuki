__version__ = "2.2.6"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

from .Database import Database

__all__ = ['Database']
