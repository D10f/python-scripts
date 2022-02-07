#! /usr/bin/python3

from pprint import pprint

import argparse
import logging
import pathlib
import shutil
import sys
import re

# DEFAULT HOME DIRECTORIES

HOME_DIR      = pathlib.Path.home()
DOWNLOAD_DIR  = pathlib.Path(HOME_DIR, 'Downloads')
DOCUMENTS_DIR = pathlib.Path(HOME_DIR, 'Documents')
PICTURES_DIR  = pathlib.Path(HOME_DIR, 'Pictures')
MUSIC_DIR     = pathlib.Path(HOME_DIR, 'Music')
VIDEOS_DIR    = pathlib.Path(HOME_DIR, 'Videos')

# DEFAULT FILE ASSOCIATIONS

FILE_EXT_ASSOCIATIONS = {
  DOCUMENTS_DIR: set([
    'txt',
    'md',
    'pdf',
    'doc',
    'docx',
    'xls',
    'xlsx',
    'ppt',
    'pptx',
    'odt',
    'ods',
    'odp',
    'odg'
  ]),
  PICTURES_DIR: set([
    'jpg',
    'jpeg',
    'png',
    'svg',
    'gif',
    'tif',
    'tiff',
    'psd',
    'webp',
    'avif'
  ]),
  MUSIC_DIR: set([
    'mov',
    'mkv',
    'mp3'
  ]),
  VIDEOS_DIR: set([
    'mp4',
    'wav'
  ]),
}


def main():
  args = parse_arguments()

  if args.map:
    update_file_associations(args.map)
  
  # pprint(FILE_EXT_ASSOCIATIONS)
  print_arguments(args)


def update_file_associations(custom_map):
  'Updates the default list of file associated to a specific directory'

  for mapping in custom_map:
    [custom_dir_input, file_extension_input] = mapping.split('=')
    
    custom_dir_path = pathlib.Path(custom_dir_input).resolve()
    file_extensions = file_extension_input.split(',')

    # Remove extensions from existing association object
    for directory in FILE_EXT_ASSOCIATIONS:
      FILE_EXT_ASSOCIATIONS[directory].difference_update(file_extensions)
    
    # Create or update entry with the extensions as specified
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

  logging.debug(f'Running as user: {pathlib.os.getenv("USER")}')
  logging.debug(f'Running with arguments: {args}')
  logging.info(f'Reading from: {args.src_directory}')
  
  if args.ignore:
    logging.info(f'Ignoring extensions: {args.ignore}')

  if args.only:
    logging.info(f'Running only for extensions: {args.only}')

  if args.map:
    logging.info(f'Using custom file associations:')
    [print(pathlib.Path(x).resolve()) for x in args.map]

  if args.verbose > 1:
    logging.debug(f'Using file associations')
    for directory in FILE_EXT_ASSOCIATIONS:
      print(directory, end='\n\t')
      print(FILE_EXT_ASSOCIATIONS[directory])


def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('-s', '--src_directory',
    help='Source directory to read files from. Defaults to ~/Downloads',
    type=pathlib.Path,
    default=DOWNLOAD_DIR
  )

  file_ext_options = parser.add_mutually_exclusive_group()
  file_ext_options.add_argument('-o', '--only',
    help='Performs the action only on the specified extensions',
    nargs='+',
    metavar='extension  '
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
  
  parser.add_argument('-x', '--ignore-files',
    help='Ignores specific filenames',
    nargs='+',
    metavar='filename'
  )

  parser.add_argument('-m', '--map',
    help='Overwrite custom file extension to a specific path',
    nargs=1,
    metavar='dir=ext1,ext2',
    action='extend'
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