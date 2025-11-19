__version__ = "1.0.1"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

from .Browser import Browser

__all__ = ['Browser']
