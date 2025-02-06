import functools
import warnings

def deprecated(deprecated_version, new_alternative: str):
    """
    Decorator per marcare una funzione (o metodo) come deprecata.
    Quando la funzione viene chiamata, viene emesso un DeprecationWarning.

    Args:
        deprecated_version (str): La versione in cui la funzione è stata deprecata.
        new_alternative (str): Indicazione della nuova opzione o funzione da usare.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} è deprecata dalla versione {deprecated_version}. Utilizzare {new_alternative} al suo posto."
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
