__version__ = "2.1.1"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()
from .Http import Http, InsufficientInfo, MethodNotSupported

__all__ = ['Http', 'InsufficientInfo', 'MethodNotSupported']
