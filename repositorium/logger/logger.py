#!/usr/bin/env python3

import logging

class Logger:

  _verbosity = 0

  @property
  def verbosity(cls):
    """The root directory of the repository"""
    return cls._entrypoint
  
  @verbosity.setter
  def verbosity(cls, verbosity):
    """Adjusts the verbosity output used when creating loggers"""
    _verbosity = verbosity

  @classmethod
  def create_logger(cls, name):
    """Creates a new logger with the given name provided and custom formatting"""

    logger = logging.getLogger(name)
    stdout_handler = logging.StreamHandler()
    
    fmt = '%(asctime)s [ %(levelname)s ] %(message)s'
    datefmt = None

    if cls.verbosity == 1:
      logger.setLevel(logging.INFO)
      datefmt = '%Y-%m-%d %H:%M'
    elif cls.verbosity > 1:
      logger.setLevel(logging.DEBUG)
      fmt = "%(asctime)s [ %(levelname)s - %(filename)s ] %(message)s"

    stdout_handler.setFormatter(CustomFormatter(fmt, datefmt))
    logger.addHandler(stdout_handler)

    return logger

# Custom format class to print using colors. Credit:
# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/

class CustomFormatter(logging.Formatter):
  """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

  gray = '\x1b[38;5;240m'
  blue = '\x1b[38;5;39m'
  yellow = '\x1b[38;5;220m'
  orange = '\x1b[38;5;202m'
  red = '\x1b[38;5;160m'
  reset = '\x1b[0m'

  def __init__(self, fmt, datefmt):
    super().__init__()
    self.fmt = fmt
    self.datefmt = datefmt
    self.FORMATS = {
      logging.DEBUG: f'{self.gray}{self.fmt}{self.reset}',
      logging.INFO: f'{self.blue}{self.fmt}{self.reset}',
      logging.WARNING: f'{self.yellow}{self.fmt}{self.reset}',
      logging.ERROR: f'{self.orange}{self.fmt}{self.reset}',
      logging.CRITICAL: f'{self.red}{self.fmt}{self.reset}',
    }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt, self.datefmt)
    return formatter.format(record)