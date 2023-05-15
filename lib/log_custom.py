import logging

class CustomFormatter(logging.Formatter):

    grey   = "\x1b[38;20m"
    yellow = "\x1b[43;1m"
    green  = "\x1b[32;1m"
    red    = "\x1b[31;20m"
    bold_red = "\x1b[41m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: green + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)