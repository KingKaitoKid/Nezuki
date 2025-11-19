import os, sys, json, logging
from logging.handlers import TimedRotatingFileHandler
from coloredlogs import ColoredFormatter

_nezuki_logger = None  # singleton globale


# -------------------
# Config di base
# -------------------
DEFAULT_CONFIG = {
    "level": logging.DEBUG,
    "console": {
        "enabled": True,
        "level": logging.DEBUG,
        "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(context)s - %(internal_str)s - %(message)s"
    },
    "file": {
        "enabled": False,  # 🔄 fallback: no file se non specificato
        "filename": None,
        "level": logging.INFO,
        "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(context)s - %(internal_str)s - %(message)s",
        "maxBytes": 100 * 1024 * 1024,
        "backupCount": 5,
        "when": "D",
        "interval": 30
    }
}


# -------------------
# Utilities
# -------------------
def merge_configs(user_config: dict | None) -> dict:
    """Unisce config utente con quella di default."""
    cfg = DEFAULT_CONFIG.copy()
    if user_config:
        for key, val in user_config.items():
            if isinstance(val, dict) and key in cfg:
                cfg[key].update(val)
            else:
                cfg[key] = val
    return cfg


class CallerInfoFilter(logging.Filter):
    def filter(self, record):
        record.internal_str = "[INTERNAL]" if getattr(record, "internal", False) else "[USER]"
        record.context = f"{record.filename}::{record.funcName}"
        return True


class SizeAndTimeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when="D", interval=30, backupCount=5, maxBytes=100*1024*1024, **kwargs):
        self.maxBytes = maxBytes
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, **kwargs)

    def shouldRollover(self, record):
        return (
            super().shouldRollover(record)
            or (os.path.exists(self.baseFilename) and os.stat(self.baseFilename).st_size >= self.maxBytes)
        )


# -------------------
# Costruzione logger
# -------------------
def _build_logger(config: dict) -> logging.Logger:
    config = merge_configs(config)
    logger = logging.getLogger("Nezuki")
    logger.setLevel(config["level"])
    logger.propagate = False
    logger.handlers.clear()
    logger.addFilter(CallerInfoFilter())

    # Console
    if config["console"]["enabled"]:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(config["console"]["level"])
        ch.setFormatter(ColoredFormatter(config["console"]["formatter"]))
        logger.addHandler(ch)

    # File
    if config["file"]["enabled"] and config["file"]["filename"]:
        os.makedirs(os.path.dirname(config["file"]["filename"]), exist_ok=True)
        fh = SizeAndTimeRotatingFileHandler(
            filename=config["file"]["filename"],
            when=config["file"]["when"],
            interval=config["file"]["interval"],
            backupCount=config["file"]["backupCount"],
            maxBytes=config["file"]["maxBytes"],
        )
        fh.setLevel(config["file"]["level"])
        fh.setFormatter(logging.Formatter(config["file"]["formatter"]))
        fh.addFilter(CallerInfoFilter())
        logger.addHandler(fh)

    return logger


# -------------------
# API pubblica
# -------------------
def configure_nezuki_logger(config: dict | None = None):
    """Forza configurazione custom del logger."""
    global _nezuki_logger
    _nezuki_logger = _build_logger(config)

def get_nezuki_logger() -> logging.Logger:
    """Restituisce logger pronto: se non configurato, fallback automatico."""
    global _nezuki_logger
    if _nezuki_logger is None:
        # fallback: prova da env, altrimenti console-only
        json_path = os.getenv("NEZUKILOGS")
        if json_path and os.path.exists(json_path):
            with open(json_path) as f:
                config = json.load(f)
        else:
            config = None
        _nezuki_logger = _build_logger(config)
    return _nezuki_logger
