import functools, warnings
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
            msg = f"{func.__name__} è deprecata, supporto garantito fino alla versione {deprecated_version}, ora sei alla versione {func.__version__}. {new_alternative} al suo posto."
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            logger.warning(f"DEPRECATION WARNING: {msg}", extra={"internal": True})
            return func(*args, **kwargs)
        return wrapper
    return decorator
