#! /usr/bin/python3

'''
file_organizer.py - Keep your files under control automatically. Run this script and let it decide where to send those files inside the messy Downlods folder.
                    Trust the defaults or customize away as much as you want to move only those files that you really care about.

usage: file_organizer.py [-h] [-s SRC] [-o extension [extension ...] | -i extension [extension ...]] [-f] [-e regexp] [-m dir=.ext1,.ext2] [--dry-run] [-v]
                         [--version]

optional arguments:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     Source directory to read files from. Defaults to ~/Downloads
  -o extension [extension ...], --only extension [extension ...]
                        Performs the action only on the specified extensions
  -i extension [extension ...], --ignore extension [extension ...]
                        Ignores the specified file extensions
  -f, --force           Overwrites existing files in target directory
  -e regexp, --regexp regexp
                        Uses regular expression matching to filter down results.
  -m dir=.ext1,.ext2, --map dir=.ext1,.ext2
                        Overwrite custom file extension to a specific path
  --dry-run             Runs the script without writing changes to disk
  -v, --verbose         Produce extended output
  --version             show program's version number and exit


examples:

Move only files with extension mp4 and wav ignore the rest
./file_organizer.py -o mp4 wav

Do not move files with extensions mp4 wav
./file_organizer.py -i mp4 wav

Move epub and pdf files to ~/Sync/Books (default for those two is ~/Documents)
./file_organizer.py -m ~/Sync/Books=epub,pdf

Move only epub files to ~/Sync/Books (default for those two is ~/Documents)
./file_organizer.py -o epub -m ~/Sync/Books=epub,pdf

Move files from ~/Desktop (default is to move from ~/Downloads)
./file_organizer.py -s ~/Desktop

Only move files that start with "distr", case sensitive e.g.: Distributed_Systems_With_Node_js.epub
./file_organizer.py -e '^Distr'

Run in test mode to verify changes before actually writing to disk
./file_organizer.py --dry-run

Check script's version
./file_organizer.py --version
'''

# TODO: Allow using -f to force overwrite existing files, or create copies
# TODO: Create missing directories when specified as destination source for moved files
# TODO: Improve dry-run output for clarity

from pathlib import Path
import argparse
import logging
import shutil
import os
import re

CURRENT_VERSION = 'v0.0.2'

# DEFAULT HOME DIRECTORIES

HOME_DIR      = Path.home()
DOWNLOAD_DIR  = Path(HOME_DIR, 'Downloads')
DOCUMENTS_DIR = Path(HOME_DIR, 'Documents')
PICTURES_DIR  = Path(HOME_DIR, 'Pictures')
PROJECTS_DIR  = Path(HOME_DIR, 'Projects')
MUSIC_DIR     = Path(HOME_DIR, 'Music')
VIDEOS_DIR    = Path(HOME_DIR, 'Videos')

# DEFAULT FILE ASSOCIATIONS

FILE_EXT_ASSOCIATIONS = {
  DOCUMENTS_DIR: set([
    '.txt',
    '.md',
    '.pdf',
    '.doc',
    '.docx',
    '.xls',
    '.xlsx',
    '.ppt',
    '.pptx',
    '.odt',
    '.ods',
    '.odp',
    '.odg',
    '.epub',
    '.mobi',
    '.azw',
  ]),
  PROJECTS_DIR: set([
    '.apk',
    '.jar',
    '.cmd',
    '.exe',
    '.bin',
    '.sh',
    '.bat',
    '.app',
    '.appimage',
    '.deb',
    '.snap',
  ]),
  PICTURES_DIR: set([
    '.jpg',
    '.jpeg',
    '.png',
    '.svg',
    '.gif',
    '.tif',
    '.tiff',
    '.psd',
    '.webp',
    '.avif',
    '.bmp',
    '.favicon',
    '.raw',
  ]),
  MUSIC_DIR: set([
    '.wav',
    '.wave',
    '.aif',
    '.mp3',
    '.mid',
    '.midi',
    '.flac',
    '.omg',
    '.ogg',
  ]),
  VIDEOS_DIR: set([
    '.mpeg',
    '.mpg',
    '.mov',
    '.wmv',
    '.mp4',
    '.mkv',
    '.webm',
    '.ogv',
  ]),
}

# INITIALIZE LOGGER INSTANCE

logger = logging.getLogger(__name__)


def main():
  args = parse_arguments()
  setup_logger(args.verbose)

  if args.map:
    update_file_associations(args.map)
  
  target_files = select_files(
    args.src,
    ignore_extensions = args.ignore,
    only_extensions = args.only,
    pattern = args.pattern
  )

  print_arguments(args)

  move_files(target_files, force = args.force, dry = args.dry)


def move_files(files, force = False, dry = False):
  """Moves files based on their extension to the associated directory"""

  for file in files:
    for directory in FILE_EXT_ASSOCIATIONS:
      if ''.join(file.suffixes) in FILE_EXT_ASSOCIATIONS[directory]:
        file_already_exists = is_file_in_dir(file.name, directory)

        if file_already_exists and not force:
          logger.warning(f'Destination path {Path.joinpath(directory, file.name)} already exists. Skipping...')
          continue

        if not dry:
          # path-like objects only supported on Python3.9+
          shutil.move(str(file), str(directory))

        logger.info(f'Moving {file} to {directory}')
        
        if file_already_exists:
          logger.warning(f'-f flag provided! Overwriting {Path.joinpath(directory, file.name)}')

        continue


def is_file_in_dir(filename, directory):
  """Checks if the provided filename already exists in the given directory"""

  return filename in [x.name for x in Path.iterdir(directory)]


def select_files(src_dir, ignore_extensions = None, only_extensions = None, pattern = None):
  """Selects the files matching the filter criteria passed as arguments"""

  # ignore files without extension (includes directories)
  src_dir_files = [x for x in Path.iterdir(src_dir) if x.suffix]

  # Pre-prend extension list with a dot if it was not provided
  if only_extensions:
    ext_filters = [f'.{ext}' if not ext.startswith('.') else ext for ext in only_extensions]
    src_dir_files = [x for x in src_dir_files if x.suffix in ext_filters]

  if ignore_extensions:
    ext_filters = [f'.{ext}' if not ext.startswith('.') else ext for ext in ignore_extensions]
    src_dir_files = [x for x in src_dir_files if x.suffix not in ext_filters]

  # Combine stem and suffix to get full filename, including multiple extensions
  if pattern:
    regexp = re.compile(pattern)
    src_dir_files = [x for x in src_dir_files if regexp.search(f'{x.stem}{x.suffix}')]

  return src_dir_files


def update_file_associations(custom_map):
  """Updates the default list of file associated to a specific directory"""

  for mapping in custom_map:
    [custom_dir_input, file_extension_input] = mapping.split('=')
    
    custom_dir_path = Path(custom_dir_input).resolve()

    # Prefix them with a dot if it was not provided as arguments
    file_extensions = [f'.{ext}' if not ext.startswith('.') else ext for ext in file_extension_input.split(',')]

    # Remove extensions from existing sets
    for directory in FILE_EXT_ASSOCIATIONS:
      FILE_EXT_ASSOCIATIONS[directory].difference_update(file_extensions)
    
    # Create or update set with the extensions as specified
    if custom_dir_path in FILE_EXT_ASSOCIATIONS:
      FILE_EXT_ASSOCIATIONS[custom_dir_path].update(file_extensions)
    else:
      FILE_EXT_ASSOCIATIONS[custom_dir_path] = set(file_extensions)


def setup_logger(verbosity):
  """Defines the handler and formatter for the module's logger instance."""

  # Define handler (output to console) based on verbosity provided
  stdout_handler = logging.StreamHandler()
  if verbosity == 1:
    stdout_handler.setLevel(logging.INFO)
  elif verbosity == 2:
    stdout_handler.setLevel(logging.DEBUG)
  else:
    stdout_handler.setLevel(logging.WARNING)

  # Define formatter for the handler
  fmt = '%(asctime)s | %(module)s line %(lineno)3d | %(levelname)8s | %(message)s'

  # Custom format class to print using colors. Credit:
  # https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/

  class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    debug = '\x1b[38;21m'
    info = '\x1b[38;5;39m'
    warning = '\x1b[38;5;220m'
    error = '\x1b[38;5;202m'
    critical = '\x1b[38;5;160m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
      super().__init__()
      self.fmt = fmt
      self.FORMATS = {
        logging.DEBUG: self.debug + self.fmt + self.reset,
        logging.INFO: self.info + self.fmt + self.reset,
        logging.WARNING: self.warning + self.fmt + self.reset,
        logging.ERROR: self.error + self.fmt + self.reset,
        logging.CRITICAL: self.critical + self.fmt + self.reset
      }

    def format(self, record):
      log_fmt = self.FORMATS.get(record.levelno)
      formatter = logging.Formatter(log_fmt)
      return formatter.format(record)

  stdout_handler.setFormatter(CustomFormatter(fmt))
  logger.addHandler(stdout_handler)
  

def print_arguments(args):
  """Prints the arugments the script uses to run, if verbosity is specified"""

  logger.debug(f'Running as user: {os.getenv("USER")}')
  logger.debug(f'Running with arguments: {args}')
  logger.info(f'Reading from: {args.src}')
  
  if args.ignore:
    logger.info(f'Ignoring extensions: {args.ignore}')

  if args.only:
    logger.info(f'Running only for extensions: {args.only}')
  
  if args.pattern:
    logger.info(f'Looking files matching pattern: {args.pattern}')

  if args.map:
    logger.info(f'Using custom file associations:')
    [print(Path(x).resolve()) for x in args.map]

  if args.force:
    logger.info(f'Running with force option enabled.')
  
  if args.dry:
    logger.warning(f"Running in test mode. Changes won't be saved to disk.")

  if args.verbose > 1:
    logger.debug(f'Using file associations')
    for directory in FILE_EXT_ASSOCIATIONS:
      print(directory, end='\n\t')
      print(FILE_EXT_ASSOCIATIONS[directory])


def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('-s', '--src',
    help='Source directory to read files from. Defaults to ~/Downloads',
    type=Path,
    default=DOWNLOAD_DIR
  )

  file_ext_options = parser.add_mutually_exclusive_group()
  file_ext_options.add_argument('-o', '--only',
    help='Performs the action only on the specified extensions',
    nargs='+',
    metavar='extension'
  )
  file_ext_options.add_argument('-i', '--ignore',
    help='Ignores the specified file extensions',
    nargs='+',
    metavar='extension'
  )

  parser.add_argument('-f', '--force',
    help='Overwrites existing files in target directory',
    action='store_true'
  )
  
  parser.add_argument('-e', '--regexp',
    help='Uses regular expression matching to filter down results.',
    dest='pattern',
    metavar='regexp',
  )

  parser.add_argument('-m', '--map',
    help='Overwrite custom file extension to a specific path',
    nargs=1,
    metavar='dir=.ext1,.ext2',
    action='extend'
  )

  parser.add_argument('--dry-run',
    help='Runs the script without writing changes to disk',
    action='store_true',
    dest='dry'
  )

  parser.add_argument('-v', '--verbose',
    help='Produce extended output',
    action='count',
    default=0
  )

  parser.add_argument('--version',
    action='version',
    version=f'%(prog)s {CURRENT_VERSION}'
  )

  return parser.parse_args()


if __name__ == '__main__':
  main()