from . import __version__
import functools, warnings, inspect
from packaging import version
from nezuki import __version__ as nezuki_version
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()
__version__ = __version__

def legacy(introduced_in: str = None, note: str = None, removed_in: str = None):
    """
    Marca una funzione come legacy (compatibilità storica).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                module = inspect.getmodule(func)
                local_version = getattr(module, "__version__", nezuki_version)
            except Exception:
                local_version = nezuki_version
            current = version.parse(local_version)
            removed_v = version.parse(removed_in) if removed_in else None

            msg = (
                f"{func.__name__}() è una funzione legacy. "
                f"Versione corrente: {current}. "
                + (f"Introdotta in {introduced_in}. " if introduced_in else "")
                + (f"Verrà rimossa in {removed_in}. " if removed_in else "")
                + (f"Note: {note}." if note else "")
            )

            if removed_v and current >= removed_v:
                logger.error(f"LEGACY ERROR: {msg}", extra={"internal": True})
                raise RuntimeError(msg)
            else:
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                logger.warning(f"LEGACY WARNING: {msg}", extra={"internal": True})

            return func(*args, **kwargs)

        _add_note(func, f"[LEGACY fino a {removed_in or '∞'}] {note or ''}")
        return wrapper
    return decorator


def _add_note(func, note: str):
    if func.__doc__:
        func.__doc__ += f"\n\n⚠️ {note}"
    else:
        func.__doc__ = f"⚠️ {note}"
