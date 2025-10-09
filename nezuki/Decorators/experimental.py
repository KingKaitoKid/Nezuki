from . import __version__
import functools
import warnings
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()
__version__ = __version__

def experimental(added_in: str = None, notes: str = None, expected_stable_in: str = None):
    """
    Marca una funzione come sperimentale. Potrebbe cambiare o essere rimossa.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = (
                f"{func.__name__}() è sperimentale. "
                + (f"Aggiunta in {added_in}. " if added_in else "")
                + (f"Prevista stabile in {expected_stable_in}. " if expected_stable_in else "")
                + (f"{notes or ''}")
            )
            warnings.warn(msg, category=UserWarning, stacklevel=2)
            logger.warning(f"EXPERIMENTAL NOTICE: {msg}", extra={"internal": True})
            return func(*args, **kwargs)

        _add_note(func, f"[EXPERIMENTAL] {notes or ''}")
        return wrapper
    return decorator


def _add_note(func, note: str):
    if func.__doc__:
        func.__doc__ += f"\n\n⚠️ {note}"
    else:
        func.__doc__ = f"⚠️ {note}"
