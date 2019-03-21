"""Helper to define own logger."""
import logging

# each logger of specified name is singleton.
_loggers = {}


def get_logger(name):
    """
    Get logger of specified name.

    The logger has configured :class:`logging.StreamHandler` and default logging level set to *ERROR*. Output is
    formatted as ``[%(levelname)s] - %(name)s - %(message)s``.

    :param str name:    Name of the logger

    :return: Instance of the logger
    :rtype: :class:`logging.Logger`
    """
    global loggers
    if _loggers.get(name):
        return _loggers.get(name)
    else:
        logger = logging.getLogger(name)
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(logging.NOTSET)
        logger.addHandler(ch)
        logger.propagate = False
        _loggers[name] = logger
    return logger
