import os, sys, json, logging, contextvars, re, uuid, time
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler


# =========================
# Singleton globale
# =========================
_nezuki_logger = None

# =========================
# Livelli custom
# =========================
TRACE_LEVEL = 5
SUCCESS_LEVEL = 25
logging.addLevelName(TRACE_LEVEL, "TRACE")
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def _logger_trace(self, msg, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, msg, args, **kwargs)

def _logger_success(self, msg, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, msg, args, **kwargs)

logging.Logger.trace = _logger_trace
logging.Logger.success = _logger_success

# =========================
# Config di base
# =========================
DEFAULT_CONFIG = {
    "level": logging.DEBUG,
    "console": {
        "enabled": True,
        "level": logging.DEBUG,
        # style: "colored" | "plain" | "json" | <format string>
        "style": "colored",
        "format": "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(context)s | %(internal_str)s | %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "file": {
        "enabled": False,
        "filename": None,
        "level": logging.INFO,
        # style: "plain" | "json" | <format string>
        "style": "plain",
        "format": "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(process)d:%(threadName)s | %(context)s | %(internal_str)s | %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "maxBytes": 100 * 1024 * 1024,
        "backupCount": 5,
        "when": "D",
        "interval": 30
    },
    # opzionale: file separato per WARNING+
    "error_file": {
        "enabled": False,
        "filename": None,
        "level": logging.WARNING,
        "style": "plain",
        "format": "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(context)s | %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "maxBytes": 50 * 1024 * 1024,
        "backupCount": 7,
        "when": "D",
        "interval": 7
    },
    # Filtri di rumore (nomi di logger da abbassare)
    "noise": {
        "urllib3": logging.WARNING,
        "botocore": logging.ERROR,
        "asyncio": logging.ERROR
    }
}

# =========================
# Context ID (Correlation)
# =========================
_context_id_var = contextvars.ContextVar("nezuki_request_id", default=None)
_last_log_time = contextvars.ContextVar("nezuki_last_log_time", default=0.0)

REQUEST_EXPIRATION_SECONDS = 2.0  # rigenera ID se inattivo da >2s
SENSITIVE_PATTERNS = [
        re.compile(r"(?i)(password\s*[:=]?\s*)(\S+)", re.UNICODE),
        re.compile(r"(?i)(token\s*[:=]?\s*)(\S+)", re.UNICODE),
        re.compile(r"(?i)(api[_\-]?key\s*[:=]?\s*)(\S+)", re.UNICODE),
        re.compile(r"(?i)(secret\s*[:=]?\s*)(\S+)", re.UNICODE),
        re.compile(r"(?i)(authorization\s*[:=]?\s*)(\S+)", re.UNICODE)
    ]

def get_request_id() -> str:
    """Restituisce l'ID della richiesta corrente, generandolo se serve."""
    rid = _context_id_var.get()
    last = _last_log_time.get()
    now = time.time()

    if not rid or (now - last > REQUEST_EXPIRATION_SECONDS):
        rid = f"req-{uuid.uuid4().hex[:8]}"
        _context_id_var.set(rid)
    _last_log_time.set(now)
    return rid

def clear_request_id():
    """Resetta manualmente il request_id (usato raramente)."""
    _context_id_var.set(None)
    _last_log_time.set(0.0)

def set_context_id(value: str | None):
    """Imposta un correlation id (es. per una richiesta HTTP)."""
    _context_id_var.set(value)

def get_context_id() -> str | None:
    return _context_id_var.get()

# =========================
# CONTEXT MANAGER GLOBALE
# =========================
_context_data_var = contextvars.ContextVar("nezuki_context_data", default={})

def set_context(**kwargs):
    """Imposta o aggiorna variabili di contesto (user_id, request_id, session_id...)."""
    current = _context_data_var.get().copy()
    current.update(kwargs)
    _context_data_var.set(current)

def clear_context():
    """Pulisce il contesto per thread/request corrente."""
    _context_data_var.set({})

def get_context() -> dict:
    """Restituisce il contesto corrente."""
    return _context_data_var.get().copy()

def with_context(**kwargs):
    """Decorator/context manager per associare temporaneamente un contesto."""
    def decorator(func):
        def wrapper(*args, **inner_kwargs):
            token = _context_data_var.set({**get_context(), **kwargs})
            try:
                return func(*args, **inner_kwargs)
            finally:
                _context_data_var.reset(token)
        return wrapper
    return decorator


# =========================
# Utilities
# =========================
def merge_configs(user_config: dict | None) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy semplice
    if user_config:
        for key, val in user_config.items():
            if isinstance(val, dict) and key in cfg and isinstance(cfg[key], dict):
                cfg[key].update(val)
            else:
                cfg[key] = val
    return cfg

class SensitiveDataFilter(logging.Filter):
    """Maschera dati sensibili nei messaggi (password, token, secret, ecc.)."""

    def filter(self, record):
        msg = record.getMessage()
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub(r"\1********", msg)
        record.msg = msg
        return True

class CallerInfoFilter(logging.Filter):
    def filter(self, record):
        record.internal_str = "[INTERNAL]" if getattr(record, "internal", False) else "[USER]"
        record.context = f"{record.filename}::{record.funcName}"
        record.request_id = get_request_id()
        return True


class SizeAndTimeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when="D", interval=30, backupCount=5, maxBytes=100*1024*1024, **kwargs):
        self.maxBytes = maxBytes
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, **kwargs)

    def shouldRollover(self, record):
        time_roll = super().shouldRollover(record)
        size_roll = os.path.exists(self.baseFilename) and os.stat(self.baseFilename).st_size >= self.maxBytes
        return time_roll or size_roll

# =========================
# Formatter
# =========================
# ANSI colori per livelli
LEVEL_COLORS = {
    "TRACE": "\033[38;5;244m",    # grigio
    "DEBUG": "\033[36m",          # ciano
    "INFO": "\033[32m",           # verde
    "SUCCESS": "\033[92m",        # verde chiaro
    "WARNING": "\033[33m",        # giallo
    "ERROR": "\033[31m",          # rosso
    "CRITICAL": "\033[41m\033[97m"  # fondo rosso + testo bianco
}
RESET = "\033[0m"

class ColoredFormatter(logging.Formatter):
    RESET_ALL = "\033[0m"
    RESET_BG  = "\033[49m"  # reset solo sfondo

    LEVEL_STYLES = {
        "TRACE":    {"badge_fg": 250, "badge_bg": 236, "text_fg": 244},
        "DEBUG":    {"badge_fg": 15,  "badge_bg": 20,  "text_fg": 39},
        "INFO":     {"badge_fg": 15,  "badge_bg": 28,  "text_fg": 34},
        "SUCCESS":  {"badge_fg": 15,  "badge_bg": 34,  "text_fg": 82},
        "WARNING":  {"badge_fg": 16,  "badge_bg": 220, "text_fg": 214},
        "ERROR":    {"badge_fg": 15,  "badge_bg": 88,  "text_fg": 196},
        "CRITICAL": {"badge_fg": 15,  "badge_bg": 52,  "text_fg": 199},
    }

    def __init__(self, fmt=None, datefmt=None, use_color=True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color and sys.stdout.isatty()

    def _fg(self, code): return f"\033[38;5;{code}m" if code is not None else ""
    def _bg(self, code): return f"\033[48;5;{code}m" if code is not None else ""

    def format(self, record):
        base = super().format(record)
        if not self.use_color:
            return base

        st = self.LEVEL_STYLES.get(record.levelname, {})
        badge_fg = self._fg(st.get("badge_fg"))
        badge_bg = self._bg(st.get("badge_bg"))
        text_fg  = self._fg(st.get("text_fg"))

        # 1) Badge con sfondo e testo del badge
        # 2) RESET SOLO SFONDO
        # 3) IMMEDIATAMENTE dopo, imposta il colore del testo per il resto della riga
        badge = f"{badge_bg}{badge_fg}[ {record.levelname:<7}] {self.RESET_BG}{text_fg}"

        # Sostituisci solo la prima occorrenza del levelname
        out = base.replace(record.levelname, badge, 1)

        # Chiudi tutto a fine riga
        return f"{out}{self.RESET_ALL}"



class JsonFormatter(logging.Formatter):
    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def mask_sensitive(self, msg: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub(r"\1********", msg)
        return msg

    def format(self, record):
        msg = record.getMessage()
        msg = self.mask_sensitive(msg)

        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": msg,
            "request_id": getattr(record, "request_id", None),
            "context": getattr(record, "context", None),
            "file": record.filename,
            "func": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.threadName,
            "internal": getattr(record, "internal", False)
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)

def _build_formatter(style: str, fmt: str, datefmt: str, colored_forced: bool | None = None) -> logging.Formatter:
    # style può essere: "colored" | "plain" | "json" | <format string custom>
    if style == "json":
        return JsonFormatter()
    if style == "colored":
        return ColoredFormatter(fmt=fmt, datefmt=datefmt, use_color=True if colored_forced is None else colored_forced)
    if style == "plain":
        return logging.Formatter(fmt=fmt, datefmt=datefmt)
    # se style è un format string custom, usalo direttamente
    if "%" in style or "{" in style:
        return logging.Formatter(fmt=style, datefmt=datefmt)
    # fallback
    return logging.Formatter(fmt=fmt, datefmt=datefmt)

# =========================
# Costruzione logger
# =========================
def _apply_noise_levels(noise_cfg: dict):
    for name, lvl in (noise_cfg or {}).items():
        try:
            logging.getLogger(name).setLevel(lvl)
        except Exception:
            pass

def _ensure_dir(path: str | None):
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)

def _build_logger(config: dict | None) -> logging.Logger:
    cfg = merge_configs(config)
    logger = logging.getLogger("Nezuki")
    logger.setLevel(cfg["level"])
    logger.propagate = False
    logger.handlers.clear()
    logger.addFilter(CallerInfoFilter())

    # Console
    if cfg["console"]["enabled"]:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(cfg["console"]["level"])
        ch.setFormatter(_build_formatter(
            style=cfg["console"]["style"],
            fmt=cfg["console"]["format"],
            datefmt=cfg["console"]["datefmt"]
        ))
        ch.addFilter(SensitiveDataFilter())
        logger.addHandler(ch)

    # File
    if cfg["file"]["enabled"] and cfg["file"]["filename"]:
        _ensure_dir(cfg["file"]["filename"])
        fh = SizeAndTimeRotatingFileHandler(
            filename=cfg["file"]["filename"],
            when=cfg["file"]["when"],
            interval=cfg["file"]["interval"],
            backupCount=cfg["file"]["backupCount"],
            maxBytes=cfg["file"]["maxBytes"],
            encoding="utf-8"
        )
        fh.setLevel(cfg["file"]["level"])
        fh.setFormatter(_build_formatter(
            style=cfg["file"]["style"],
            fmt=cfg["file"]["format"],
            datefmt=cfg["file"]["datefmt"]
        ))
        fh.addFilter(SensitiveDataFilter())
        fh.addFilter(CallerInfoFilter())
        logger.addHandler(fh)

    # Error file (WARNING+)
    if cfg["error_file"]["enabled"] and cfg["error_file"]["filename"]:
        _ensure_dir(cfg["error_file"]["filename"])
        efh = SizeAndTimeRotatingFileHandler(
            filename=cfg["error_file"]["filename"],
            when=cfg["error_file"]["when"],
            interval=cfg["error_file"]["interval"],
            backupCount=cfg["error_file"]["backupCount"],
            maxBytes=cfg["error_file"]["maxBytes"],
            encoding="utf-8"
        )
        efh.setLevel(cfg["error_file"]["level"])
        efh.setFormatter(_build_formatter(
            style=cfg["error_file"]["style"],
            fmt=cfg["error_file"]["format"],
            datefmt=cfg["error_file"]["datefmt"]
        ))
        efh.addFilter(CallerInfoFilter())
        logger.addHandler(efh)

    # Riduci rumore di librerie chiassose
    _apply_noise_levels(cfg.get("noise", {}))

    return logger

# =========================
# API pubblica (compatibili)
# =========================
def configure_nezuki_logger(config: dict | None = None):
    """Forza configurazione custom del logger."""
    global _nezuki_logger
    _nezuki_logger = _build_logger(config)


def get_nezuki_logger() -> logging.Logger:
    """Restituisce logger pronto: se non configurato, fallback automatico."""
    global _nezuki_logger
    if _nezuki_logger is None:
        # fallback: prova da env, altrimenti console-only
        cfg_path = os.getenv("NEZUKILOGS")
        config = None
        if cfg_path and os.path.exists(cfg_path):
            # supporto JSON e YAML "light"
            try:
                if cfg_path.endswith((".yml", ".yaml")):
                    import yaml  # opzionale: pyyaml
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        config = yaml.safe_load(f)
                else:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
            except Exception:
                config = None
        _nezuki_logger = _build_logger(config)
    return _nezuki_logger

# =========================
# Decoratori (fase 2-ready)
# =========================
import time
def log_call(level=logging.DEBUG):
    """Decoratore: logga ingresso/uscita e durata."""
    def deco(func):
        def wrapper(*args, **kwargs):
            log = get_nezuki_logger()
            log.log(level, f"→ Enter {func.__qualname__}", extra={"internal": True})
            t0 = time.perf_counter()
            try:
                res = func(*args, **kwargs)
                return res
            finally:
                dt = time.perf_counter() - t0
                log.log(level, f"← Exit  {func.__qualname__} ({dt:.3f}s)", extra={"internal": True})
        return wrapper
    return deco

def trace_call(func):
    """Decoratore sugar: usa livello TRACE."""
    return log_call(level=TRACE_LEVEL)(func)
