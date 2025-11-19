__version__ = "2.2.0"

from .Logger import configure_nezuki_logger as configure_nezuki_logger_old, get_nezuki_logger as get_nezuki_logger_old
from .Logger_2 import get_nezuki_logger as get_nezuki_logger, configure_nezuki_logger as configure_nezuki_logger, set_context_id, trace_call, set_context

__all__ = ['configure_nezuki_logger_old', 'get_nezuki_logger_old', 'configure_nezuki_logger', 'get_nezuki_logger', 'set_context_id', 'trace_call', 'set_context']
