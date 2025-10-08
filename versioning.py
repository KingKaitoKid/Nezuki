import functools, warnings
from packaging import version
from nezuki import __version__ as nezuki_module_version
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

def deprecated(deprecated_version: str, new_alternative: str):
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
            current = version.parse(func.__version__)
            deprecated = version.parse(deprecated_version)
            msg = (
                f"{func.__name__} è deprecata dalla versione {deprecated_version}, attualmente sei alla {current}.\t"
                f"Note: {new_alternative}"
                f"\tNezuki version: {nezuki_module_version}"
            )
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            if current > deprecated:
                logger.error(f"DEPRECATION ERROR: {msg}", extra={"internal": True})
            else:
                logger.warning(f"DEPRECATION WARNING: {msg}", extra={"internal": True})
            return func(*args, **kwargs)
        return wrapper
    return decorator
