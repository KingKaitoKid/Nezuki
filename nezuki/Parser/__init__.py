__version__ = "2.1.0"

from .Cedolini import Cedolini, BustaPaga, BustaPagaAppleNumbers
from .YAML import YamlManager as Yaml

__all__ = ['Cedolini', 'BustaPaga', 'BustaPagaAppleNumbers', 'Yaml']
