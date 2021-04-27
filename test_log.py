from logging import getLogger
from logging.config import dictConfig

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "[%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "": {"handlers": ["stdout"], "level": "INFO", "propagate": True}
    },
}


dictConfig(LOGGING)

log = getLogger()
log.debug("foo")
log.info("bar")
log.warning("baz")
