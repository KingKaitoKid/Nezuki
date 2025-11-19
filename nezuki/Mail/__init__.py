__version__ = "2.0.0"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

from .Mail import Mail

__all__ = ['Mail']