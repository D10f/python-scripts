#! /usr/bin/python3

from pprint import pprint

from pathlib import Path
import argparse
import logging
import shutil
import sys
import os
import re

# DEFAULT HOME DIRECTORIES

HOME_DIR      = Path.home()
DOWNLOAD_DIR  = Path(HOME_DIR, 'Downloads')
DOCUMENTS_DIR = Path(HOME_DIR, 'Documents')
PICTURES_DIR  = Path(HOME_DIR, 'Pictures')
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
  ]),
  MUSIC_DIR: set([
    '.mov',
    '.mkv',
    '.mp3',
  ]),
  VIDEOS_DIR: set([
    '.mp4',
    '.wav',
  ]),
}


def main():
  args = parse_arguments()
  
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
  'Moves files based on their extension to the associated directory'

  for file in files:
    for directory in FILE_EXT_ASSOCIATIONS:
      if file.suffix.lower() in FILE_EXT_ASSOCIATIONS[directory]:

        file_already_exists = is_file_in_dir(file.name, directory)

        if file_already_exists and not force:
          logging.warn(f'File {file.name} already exists in dest. Skipping...')
          continue

        if not dry:
          # path-like objects only supported on Python3.9+
          shutil.move(str(file), str(directory))          

        logging.info(f'Moving {file} to {directory}')
        
        if file_already_exists:
          logging.warn(f'-f flag provided! Overwriting {Path.joinpath(directory, file.name)}')

        continue


def is_file_in_dir(filename, directory):
  'Checks if the provided filename already exists in the given directory'

  return filename in [str(x) for x in Path.iterdir(directory)]


def select_files(src_dir, ignore_extensions = None, only_extensions = None, pattern = None):
  'Selects the files matching the filter criteria passed as arguments'

  # ignore files without extension (includes directories)
  src_dir_files = [x for x in Path.iterdir(src_dir) if x.suffix]

  # Pre-prend extension list with a dot if it was not provided
  if only_extensions:
    ext_filters = [f'.{ext}' if not ext.startswith('.') else ext for ext in only_extensions]
    src_dir_files = [x for x in src_dir_files if x.suffix in ext_filters]

  if ignore_extensions:
    ext_filters = [f'.{ext}' if not ext.startswith('.') else ext for ext in ignore_extensions]
    src_dir_files = [x for x in src_dir_files if x.suffix not in ext_filters]

  # Convert 'x' from path-like string. Use filename only for regexp lookup.
  if pattern:
    regexp = re.compile(pattern)
    src_dir_files = [x for x in src_dir_files if regexp.search(str(x.stem))]

  return src_dir_files


def update_file_associations(custom_map):
  'Updates the default list of file associated to a specific directory'

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


def print_arguments(args):
  'Prints the arugments the script uses to run, if verbosity is specified'

  if args.verbose == 0:
    return
  elif args.verbose == 1:
    logging.basicConfig(level=logging.INFO)
  else:
    logging.basicConfig(level=logging.DEBUG)

  logging.debug(f'Running as user: {os.getenv("USER")}')
  logging.debug(f'Running with arguments: {args}')
  logging.info(f'Reading from: {args.src}')
  
  if args.ignore:
    logging.info(f'Ignoring extensions: {args.ignore}')

  if args.only:
    logging.info(f'Running only for extensions: {args.only}')
  
  if args.pattern:
    logging.info(f'Looking files matching pattern: {args.pattern}')

  if args.map:
    logging.info(f'Using custom file associations:')
    [print(Path(x).resolve()) for x in args.map]

  if args.force:
    logging.info(f'Running with force option enabled.')
  
  if args.dry:
    logging.debug(f'Running with dry-run option enabled.')

  if args.verbose > 1:
    logging.debug(f'Using file associations')
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
    version='%(prog)s v0.0.1'
  )

  return parser.parse_args()


if __name__ == '__main__':
  main()