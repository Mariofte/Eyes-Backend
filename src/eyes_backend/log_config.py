# eyes_backend/logging_config.py
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = str(LOG_DIR / f"eyes_backend_{RUN_STAMP}.log")

FILE_FMT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_log_config(debug: bool = False) -> dict:
    LOG_DIR.mkdir(exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # Consola: estilo de uvicorn con colores por nivel
            "console": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s %(levelprefix)s API: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": None,  # None = colores solo si la terminal los soporta
            },
            "console_access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                "use_colors": None,
            },
            # Archivo: mismo estilo, sin colores
            "file": {
                "format": FILE_FMT,
                "datefmt": DATE_FMT,
            },
            "file_access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                "datefmt": DATE_FMT,
                "use_colors": False,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "console_access": {
                "class": "logging.StreamHandler",
                "formatter": "console_access",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "mode": "a",
                "encoding": "utf-8",
                "formatter": "file",
            },
            "file_access": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "mode": "a",
                "encoding": "utf-8",
                "formatter": "file_access",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {"level": "INFO"},  # sube a "uvicorn"
            "uvicorn.access": {
                "handlers": ["console_access", "file_access"],
                "level": "INFO",
                "propagate": False,
            },
            "eyes_backend": {
                "handlers": ["console", "file"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
        },
    }