__version__ = "1.0.0"

from .deprecated import deprecated
from .legacy import legacy
from .experimental import experimental

__all__ = ["deprecated", "legacy", "experimental"]