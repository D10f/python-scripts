import logging

class Logger:
    def __init__(self, name):
        self.logger = self.create_logger(name)
        self.logger.set_verbosity = self._set_verbosity


    def _set_verbosity(self, verbosity):
        if verbosity == 1:
            self.logger.setLevel(logging.INFO)
        if verbosity == 3:
            self.logger.setLevel(logging.DEBUG)


    def _set_format(self, verbosity):
        pass


    def has_full_date(self):
        pass


    def create_logger(self, name):
        # Create logger for a particular file
        logger = logging.getLogger(name)

        # Define output format
        format = '%(asctime)s [ %(levelname)s ] %(message)s'

        # Create handler to print to stdout
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(ColorFormat(format))
        logger.addHandler(stdout_handler)

        return logger


class ColorFormat(logging.Formatter):
    '''
    Logging colored formatter, adapted from:
    https://stackoverflow.com/a/56944256/3638629
    '''

    gray = '\x1b[38;5;240m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;220m'
    orange = '\x1b[38;5;202m'
    red = '\x1b[38;5;160m'
    reset = '\x1b[0m'

    def __init__(self, format):
        super().__init__()
        self.fmt = format
        self.FORMATS = {
          logging.DEBUG: f'{self.gray}{self.fmt}{self.reset}',
          logging.INFO: f'{self.blue}{self.fmt}{self.reset}',
          logging.WARNING: f'{self.yellow}{self.fmt}{self.reset}',
          logging.ERROR: f'{self.orange}{self.fmt}{self.reset}',
          logging.CRITICAL: f'{self.red}{self.fmt}{self.reset}',
        }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format)
        return formatter.format(record)
