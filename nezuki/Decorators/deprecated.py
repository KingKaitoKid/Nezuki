from . import __version__
import functools, warnings, inspect, typing
from packaging import version
from nezuki import __version__ as nezuki_module_version
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()
__version__ = __version__

def deprecated(deprecated_version: str, new_alternative: str, removed_in: str = None, tipo: typing.Literal["Funzione", "Modulo"] = "Funzione"):
    """
    Decorator per marcare una funzione (o metodo) come deprecata.
    Quando la funzione viene chiamata, viene emesso un DeprecationWarning.

    Args:
        deprecated_version (str, required): La versione in cui la funzione è stata deprecata.
        new_alternative (str, required): Indicazione della nuova opzione o funzione da usare.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                module = inspect.getmodule(func)
                local_version = getattr(module, "__version__", nezuki_module_version)
            except Exception:
                local_version = nezuki_module_version
            current = version.parse(local_version)
            deprecated = version.parse(deprecated_version)
            msg = (
                f"{tipo}: {func.__name__} (del modulo {func.__module__})\tSupporto fino a versione {deprecated_version}, in uso {current}." if tipo == "Funzione" else ''
                f"{tipo}: {func.__name__}\tSupporto fino a versione {deprecated_version}, in uso {current}." if tipo == "Modulo" else ''
                f"\tNote: {new_alternative}"
                f"\tModulo Nezuki versione: {nezuki_module_version}"
                f"\tè consigliato verificare se presente aggiornamento modulo."
                f"{f' RIMOSSA IN VERSIONE {removed_in}.' if removed_in else ''}"
            )
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            if current > deprecated:
                logger.error(f"DEPRECATION ERROR: {msg}", extra={"internal": True})
            else:
                logger.warning(f"DEPRECATION WARNING: {msg} ", extra={"internal": True})
            return func(*args, **kwargs)
        _add_note(func, f"[DEPRECATED da {deprecated_version} → {removed_in or '∞'}] {new_alternative or ''}")
        return wrapper
    return decorator

def _add_note(func, note: str):
    if func.__doc__:
        func.__doc__ += f"\n\n⚠️ {note}"
    else:
        func.__doc__ = f"⚠️ {note}"