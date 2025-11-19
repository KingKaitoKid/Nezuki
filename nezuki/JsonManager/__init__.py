__version__ = "2.0.1"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()
from .JsonManager import JsonManager

__all__ = ['JsonManager']
