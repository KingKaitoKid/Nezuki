__version__ = "2.1.2"
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

from .Cedolini import Cedolini, BustaPaga, BustaPagaAppleNumbers
from .YAML import YamlManager as Yaml


__all__ = ['Cedolini', 'BustaPaga', 'BustaPagaAppleNumbers', 'Yaml']
