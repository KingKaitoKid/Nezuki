import os
import traceback
import warnings
import functools
import sys
# from commonLogId import get_logger  # Usa il logger centralizzato


warnings.simplefilter('default', DeprecationWarning)  # Mostra tutti i DeprecationWarning

current_version = "1.0.2"

class Deprecation(Exception):
    """Eccezione lanciata quando si tenta di usare una funzione deprecata che non è più supportata."""
    def __init__(self, function_name, version):
        global current_version
        # logger.error(f"È stata usata una funzione deprecata - {function_name} è dismessa dalla versione {version}, sei alla {current_version}, non è più garantito il funzionamento corretto.")
        super().__init__(f"{function_name} è dismessa dalla versione {version}, sei alla {current_version}, non è più garantito il funzionamento corretto.")

# Decoratore per contrassegnare le funzioni come deprecate
def deprecated(deprecated_version, new_option: str):
    """
    Decorator to mark functions as deprecated. It will result in a warning being emitted when the function is used,
    and disables the function if the deprecated version is less than or equal to the current version.

    Args:
        deprecated_version (str): Version at which the function was deprecated.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # global logger
            if compare_versions(current_version, deprecated_version) >= 0:
                raise Deprecation(func.__name__, deprecated_version)
            msg = f"{func.__name__} è deprecata con la nota {new_option}"
            # Trova il chiamante
            frame = sys._getframe(1)
            code = frame.f_code
            class_name = frame.f_globals.get("__name__", "")
            function_name = code.co_name
            file_name = code.co_filename
            # logger.warning(f"Usata funzione in dismissione/deprecazione - {class_name}.{function_name} (file: {file_name}): Note correlate: {func.__name__} è deprecata con la nota {new_option}")
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Decoratore per versionare le classi
def versione(version: str):
    def decorator(cls):
        cls.versione = version
        return cls
    return decorator

# Funzione per confrontare le versioni
def compare_versions(current, deprecated) -> int:
    """ 
    Compare two version strings (e.g., '1.2.3' and '1.2.4').

    Returns:
        - -1 if `current` is less than `deprecated`: è possibile usarla in sicurezza
        - 0 if `current` is equal to `deprecated`: è deprecata
        - 1 if `current` is greater than `deprecated`: è deprecata
    """
    current_tuple = tuple(map(int, current.split('.')))
    deprecated_tuple = tuple(map(int, deprecated.split('.')))
    
    # Comparing version tuples directly
    if current_tuple < deprecated_tuple:
        return -1
    elif current_tuple > deprecated_tuple:
        return 1
    else:
        return 0

# Handler globale per errori non catturati
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Handler globale per errori non catturati."""
    # Imposta il logger centrale
    from commonLoggerSingleTon import get_logger
    logger = get_logger()
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Ottieni informazioni sull'errore
    error_message = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
    
    # Trovare il metodo e la classe dove l'errore si è verificato
    tb = exc_traceback
    while tb.tb_next:
        tb = tb.tb_next

    frame = tb.tb_frame
    code = frame.f_code
    class_name = frame.f_globals["__name__"]
    function_name = code.co_name

    # Formatta lo stack trace
    formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
    

    logger.critical(f"Errore fatale in {class_name}.{function_name}: {error_message}", extra={'esito_funzionale': 1, 'details': f"Type exception: {exc_type}<br>Exception value: {exc_value}<br>Stack trace: {formatted_traceback}"})
    # logger.error(f"Exception occurred in {class_name}.{function_name}: {error_message}", exc_info=(exc_type, exc_value, exc_traceback))
# Imposta l'handler globale
sys.excepthook = global_exception_handler

# Decoratore per loggare le eccezioni senza interrompere l'esecuzione
def log_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # global logger
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Ottieni informazioni sull'errore
            error_message = f"Exception: {exc_type.__name__}: {exc_value}"
            # Trovare il metodo e la classe dove l'errore si è verificato
            tb = exc_traceback
            while tb.tb_next:
                tb = tb.tb_next

            frame = tb.tb_frame
            code = frame.f_code
            class_name = frame.f_globals["__name__"]
            function_name = code.co_name
            # logger.error(f"Si è verificato un errore: {class_name}.{function_name} - {error_message}")
            raise
    return wrapper

# Metaclasse per decorare automaticamente tutti i metodi di una classe con log_exceptions
class LogExceptionsMeta(type):
    def __new__(cls, name, bases, dct):
        for attr, value in dct.items():
            if callable(value) and not attr.startswith("__"):
                dct[attr] = log_exceptions(value)
        return super().__new__(cls, name, bases, dct)