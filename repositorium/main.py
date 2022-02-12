#!/usr/bin/env python3

'''
repositorium.py - Analyze your git reposistory and print statistics such as
primary languages used, total commits, number of files, etc.

CREDIT: 
https://gist.github.com/ppisarczyk/43962d06686722d26d176fad46879d41
https://github.com/github/linguist/blob/master/lib/linguist/vendor.yml
https://github.com/douban/linguist
'''

import argparse
import yaml
import re
import os
from pathlib import Path

from repository.repository import Repository
# from logger.logger import Logger

CURRENT_VERSION = '0.0.1'

def main():
  args = parse_arguments()
  # Logger.verbosity = args.verbose
  # logger = Logger.create_logger(__name__)
  
  # vendor_list = read_vendor_list
  # repo = Repository(args.git_path, args.branch)
  
  with open('vendors.yml') as f:
    file = yaml.load(f, Loader = yaml.FullLoader)
  
  vendor_list = [re.compile(x) for x in file[:10]]

  # test = vendor_list[0]
  # print(bool(test.match('__pycache__')))


  for current, dirs, filenames in os.walk(args.git_path):
    pass


# def get_local_repository(path_to_repo, branch):
#   """Searches for and uses a repository in the local machine to run stats for."""
  
#   bytes_total, bytes_by_extension = count_bytes_of_code(repo_files)
  
#   top_languages = calculate_project_languages(bytes_total, bytes_by_extension)

#   logger.info(f'Counted {bytes_total} bytes across {len(repo_files)} files')

#   print(top_languages)


# def calculate_project_languages(bytes_total, bytes_by_extension, threshold = 1):
#   """Calculates the 5 most used languages based on the total bytes of file per
#   language. Returns a dict of sorted languages and their percentage."""

#   # Normalize values for extensions that are grouped under the same language.
#   count_by_language = {}

#   # Used to group together languages that have very low percentage values
#   other_languages = 0.00

#   for key, value in list(bytes_by_extension.items()):
#     language = FILE_EXTENSIONS[key]
#     count_by_language.setdefault(language, 0)
#     count_by_language[language] = count_by_language[language] + value

#   # Update data to percentage values
#   for key, value in list(count_by_language.items()):
#     percent_value = round(value * 100 / bytes_total, 2)

#     if percent_value < threshold:
#       other_languages = other_languages + percent_value
#       count_by_language.setdefault('Other', 0)
#       count_by_language['Other'] = count_by_language['Other'] + other_languages
#     else:
#       count_by_language[key] = round(value * 100 / bytes_total, 2)

#   return count_by_language


# def count_bytes_of_code(files):
#   """Counts total bytes of code from provided list of files and arranges them
#   by file extension in a dictionary.
#   """

#   bytes_total = 0
#   bytes_by_extension = {}

#   for file in files:
#     ext = file.suffix.lower()

#     if not ext or ext not in FILE_EXTENSIONS:
#       logger.debug(f'Discarding extension {ext}')
#       continue

#     bytes_by_extension.setdefault(ext, 0)

#     bytes_in_file = file.stat().st_size
#     bytes_total = bytes_total + bytes_in_file
#     bytes_by_extension[ext] = bytes_by_extension[ext] + bytes_in_file

#   return (bytes_total, bytes_by_extension)


def parse_arguments():
  """Parses command line arguments passed to run the script"""

  parser = argparse.ArgumentParser()
  
  parser.add_argument('git_path',
    help='the git repository path to the source code in the local machine.',
    type=Path,
  )
  parser.add_argument('-b', '--branch',
    help='the git branch to run this script against inside a repository',
    default=None
  )
  parser.add_argument('-v', '--verbose',
    help='Produce extended output',
    action='count',
    default=0
  )
  parser.add_argument('--version',
    action='version',
    version=f'Repositorium.py v{CURRENT_VERSION}'
  )

  return parser.parse_args()


if __name__ == '__main__':
  main()