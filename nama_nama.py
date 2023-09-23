#!/usr/bin/env python3

"""
usage: nama_nama.py input_dir [-h] [-t | -u | -l] [--prefix PREFIX]
                    [--suffix SUFFIX] [--separator {-,_, }] [--split] [-e regexp]
                    [--prune prune] [--dry-run] [-v] [--version]

Rename files in a directory uniformly, choose the pattern
    between all uppercase, all lowercase or title-case (only first letter of
    every word uppercase). Set a delimiter between words i.e.: like-this,
    like_that or 'maybe this' (defaults to space). Set prefix or suffix, ideal
    for music albums or photo collections e.g.: Iceland-{filename}

positional arguments:
  input_dir             The target directory where files should be renamed

optional arguments:
  -h, --help            show this help message and exit
  -t, --title           Turns the first letter in every word uppercase
  -u, --upper           Turns every letter uppercase
  -l, --lower           Turns every letter lowercase
  --prefix PREFIX       Adds a prefix string to every output filename
  --suffix SUFFIX       Adds a sufix string to every output filename
  --separator {-,_, }   Choose how the words in the output filename should be separated by. Defaults to a space
  --split               Replace non-alphanumeric characters with the value provided to --separator (does not apply on extension)
  -r, --recursive       Recursively runs this script on all directories found.
  -e regexp, --regexp regexp
                        Filter results with regular expression, instead of selecting all files in directory
  --prune prune         Remove any characters from the original filename before renaming it (does not apply on file extension).
  --dry-run             Runs the script without writing changes to disk
  -v, --verbose         Produce additional output
  --version             show program's version number and exit
"""

from pathlib import Path
from itertools import zip_longest
import argparse
import logging
import shutil
import sys
import os
import re


CURRENT_VERSION = '0.1.1'
SEPARATOR_CHARS = re.compile(r'[\+=\-_\.,;:<>\s\']+')


def main():
  args = parse_arguments()
  setup_logger(args)
  print_arguments(args)

  entrypoint = Path(args.input_dir).resolve()

  files = select_files(entrypoint, args.recursive, args.pattern)

  renamed_files = rename_files(files, args)

  if args.dry:
    for original, renamed in renamed_files:
      logger.debug(f'[test mode] {original.name} -> {renamed.name}')
    sys.exit()

  write_files_to_disk(renamed_files)



def write_files_to_disk(files):
  """Renames the files list at the input directory specified"""

  for original, renamed in files:
    shutil.move(original.resolve(), renamed.resolve())


def rename_files(files, args):
  """Returns a generator that yields the original and modified filenames"""

  for file in files:

    # Separate filename and extension (accounts for multiple eg.: .tar.gz)
    filename = file.stem.split('.')[0]
    ext = ''.join(file.suffixes)

    if args.split:
      filename = split_filename(filename, args.separator)

    if args.prune:
      filename = prune_filename(filename, args.prune)

    if args.title:
      filename = make_pascal_case(filename)

    if args.upper:
      filename = filename.upper()

    if args.lower:
      filename = filename.lower()

    renamed = Path(args.prefix + filename + ext + args.suffix)

    yield (file, Path.joinpath(file.parent, renamed))


def make_pascal_case(filename):
  """Converts a given string into Pascal Case"""

  # Produce "negative" lists of chars and separators, if any
  alpha = [x.title() for x in SEPARATOR_CHARS.split(filename)]
  non_alpha = SEPARATOR_CHARS.findall(filename)

  # Join them back together
  pascal_tuple = list(zip_longest(alpha, non_alpha, fillvalue=''))
  return ''.join(''.join(x) for x in [*pascal_tuple])


def split_filename(filename, split_with):
  """Splits filename"""
  return SEPARATOR_CHARS.sub(split_with, filename)


def prune_filename(filename, prune_char):
  """Removes the specified pattern from the given filename"""
  # return prune_char.sub('', filename)
  return filename.replace(prune_char, '')


def select_files(dir_path, recursive = False, pattern = None):
  """Matches all files in the provided directory and yields them"""

  if pattern:
    regexp = re.compile(pattern)

  for file in Path.iterdir(dir_path):

    if file.name.startswith('.'):
      continue

    # Ignore directories and hidden files
    if file.is_dir():
      if recursive:
        for _file in select_files(file.resolve(), recursive, pattern):
          yield _file
      continue

    if pattern and not regexp.search(file.name):
      continue

    yield file



def setup_logger(args):
  """Defines the handler and formatter for the module's logger instance."""

  verbosity = args.verbose

  if args.dry:
    verbosity = max(2, verbosity)

  if verbosity == 1:
    logger.setLevel(logging.INFO)

  if verbosity > 1:
    logger.setLevel(logging.DEBUG)

  # Define handler (output to console) based on verbosity provided
  stdout_handler = logging.StreamHandler()

  # Define formatter for the handler
  fmt = '[%(name)s] %(asctime)s %(levelname)-8s %(message)s'

  stdout_handler.setFormatter(CustomFormatter(fmt))
  logger.addHandler(stdout_handler)


def print_arguments(args):
  """Prints the arugments the script uses to run."""

  logger.debug(f'Running as user {os.getenv("USER")}')
  logger.debug(f'Running with arguments: {args}')
  logger.info(f'reading from "{args.input_dir.resolve()}"')

  if args.prefix:
    logger.info(f'Prefixing files with: "{args.prefix}"')

  if args.suffix:
    logger.info(f'Suffixing files with: "{args.suffix}"')

  if args.separator:
    logger.info(f'Separating files with: "{args.separator}"')

  if args.split:
    logger.info(f'Splitting files with: "{args.split}"')

  if args.title:
    logger.info('Using case settings: Capitilize first letter')

  if args.upper:
    logger.info('Using case settings: All uppercase')

  if args.lower:
    logger.info('Using case settings: All lowercase')

  if args.pattern:
    logger.info(f'Using pattern matching: {args.pattern}')

  if args.prune:
    logger.info(f'Deleting characters: {args.prune}')

  if args.dry:
    logger.warning("Running in test mode. Changes won't be written to disk.")


def parse_arguments():
  parser = argparse.ArgumentParser(
    description="""Rename files in a directory uniformly, choose the pattern
    between all uppercase, all lowercase or title-case (only first letter of
    every word uppercase). Set a delimiter between words i.e.: like-this,
    like_that or 'maybe this' (defaults to space). Set prefix or suffix, ideal
    for music albums or photo collections e.g.: Iceland-{filename}""",
    usage="""nama_nama.py input_dir [-h] [-t | -u | -l] [--prefix PREFIX]
                  [--suffix SUFFIX] [--separator {-,_, }] [--split] [-e regexp]
                  [--prune prune] [--dry-run] [-v] [--version]""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  casing_options = parser.add_mutually_exclusive_group()
  casing_options.add_argument('-t', '--title',
    help='Turns the first letter in every word uppercase',
    action='store_const',
    const='title',
    dest='title'
  )
  casing_options.add_argument('-u', '--upper',
    help='Turns every letter uppercase',
    action='store_const',
    const='upper',
    dest='upper'
  )
  casing_options.add_argument('-l', '--lower',
    help='Turns every letter lowercase',
    action='store_const',
    const='lower',
    dest='lower'
  )
  parser.add_argument('input_dir',
    help='The target directory where files should be renamed',
    type=Path
  )
  parser.add_argument('--prefix',
    help='Adds a prefix string to every output filename',
    default=''
  )
  parser.add_argument('--suffix',
    help='Adds a sufix string to every output filename',
    default=''
  )
  parser.add_argument('--separator',
    help="""Choose how the words in the output filename should be separated
    by. Defaults to a space""",
    choices=['-', '_', ' '],
    default=' '
  )
  parser.add_argument('--split',
    help="""Replace non-alphanumeric characters with the value provided
    to --separator (does not apply on extension)""",
    action='store_true'
  )
  parser.add_argument('-r', '--recursive',
    help="Recursively runs this script on all directories found.",
    action='store_true'
  )
  parser.add_argument('-e', '--regexp',
    help="""Filter results with regular expression, instead of selecting all
    files in directory""",
    dest='pattern',
    metavar='regexp',
  )
  parser.add_argument('--prune',
    help="""Remove any characters from the original filename before renaming
    it (does not apply on file extension).""",
    metavar='prune',
    dest='prune'
  )
  parser.add_argument('--dry-run',
    help='Runs the script without writing changes to disk',
    action='store_true',
    dest='dry'
  )
  parser.add_argument('-v', '--verbose',
    help='Produce additional output',
    action='count',
    default=0
  )
  parser.add_argument('--version',
    action='version',
    version=f'%(prog)s {CURRENT_VERSION}'
  )

  return parser.parse_args()


# INITIALIZE LOGGER INSTANCE AND CUSTOM FORMATTER
# Custom format class to print using colors. Credit:
# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/

logger = logging.getLogger('nama_nama.py')

class CustomFormatter(logging.Formatter):
  """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

  gray    = '\x1b[38;5;240m'
  blue    = '\x1b[38;5;39m'
  yellow  = '\x1b[38;5;220m'
  orange  = '\x1b[38;5;202m'
  red     = '\x1b[38;5;160m'
  reset   = '\x1b[0m'

  def __init__(self, fmt):
    super().__init__()
    self.fmt = fmt
    self.FORMATS = {
      logging.DEBUG: f'{self.gray}{self.fmt}{self.reset}',
      logging.INFO: f'{self.blue}{self.fmt}{self.reset}',
      logging.WARNING: f'{self.yellow}{self.fmt}{self.reset}',
      logging.ERROR: f'{self.orange}{self.fmt}{self.reset}',
      logging.CRITICAL: f'{self.red}{self.fmt}{self.reset}',
    }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)


if __name__ == '__main__':
  main()
