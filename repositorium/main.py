#!/usr/bin/env python3

'''
repositorium.py - Analyze your git reposistory and print statistics such as
primary languages used, total commits, number of files, etc.

CREDIT: 
https://gist.github.com/ppisarczyk/43962d06686722d26d176fad46879d41
https://github.com/github/linguist/blob/master/lib/linguist/vendor.yml
https://github.com/douban/linguist
'''

from pathlib import Path
import logging
import argparse
import sys
import re
import os
import yaml

from repository.repository import Repository
from logger.logger import Logger

CURRENT_VERSION = '0.0.1'

logger = None

def main():
  args = parse_arguments()
  Logger.verbosity = args.verbose
  logger = Logger.create_logger(__name__)
  repo = Repository(args.git_path, args.branch)
  
  logger.debug('hello world!')
  logger.info('Whats up dog?')
  logger.warning('Colibri makes noise')
  logger.error('You broke this shit man!')
  logger.critical('The bomb has been planted!')
  # with open('vendors.yml') as f:
  #   file = yaml.load(f, Loader = yaml.FullLoader)
  
  # ignore_vendor_files = [re.compile(x) for x in file[:10]]

  # pass


def get_local_repository(path_to_repo, branch):
  """Searches for and uses a repository in the local machine to run stats for."""

  # entrypoint = Path(path_to_repo).resolve()

  # if not is_git_repository(entrypoint):
  #   logger.warning(f'No git repository found in "{entrypoint}"')
  #   sys.exit(1)

  # if not branch_exist(entrypoint, branch):
  #   logger.warning(f'No git branch "{branch}" found in "{entrypoint}". Exiting...')
  #   sys.exit(1)

  # repo_files = select_files(entrypoint)
  
  bytes_total, bytes_by_extension = count_bytes_of_code(repo_files)
  
  top_languages = calculate_project_languages(bytes_total, bytes_by_extension)

  logger.info(f'Counted {bytes_total} bytes across {len(repo_files)} files')

  print(top_languages)


def calculate_project_languages(bytes_total, bytes_by_extension, threshold = 1):
  """Calculates the 5 most used languages based on the total bytes of file per
  language. Returns a dict of sorted languages and their percentage."""

  # Normalize values for extensions that are grouped under the same language.
  count_by_language = {}

  # Used to group together languages that have very low percentage values
  other_languages = 0.00

  for key, value in list(bytes_by_extension.items()):
    language = FILE_EXTENSIONS[key]
    count_by_language.setdefault(language, 0)
    count_by_language[language] = count_by_language[language] + value

  # Update data to percentage values
  for key, value in list(count_by_language.items()):
    percent_value = round(value * 100 / bytes_total, 2)

    if percent_value < threshold:
      other_languages = other_languages + percent_value
      count_by_language.setdefault('Other', 0)
      count_by_language['Other'] = count_by_language['Other'] + other_languages
    else:
      count_by_language[key] = round(value * 100 / bytes_total, 2)

  return count_by_language


# def count_lines_of_code(files):
def count_bytes_of_code(files):
  """Counts total bytes of code from provided list of files and arranges them
  by file extension in a dictionary.
  """

  bytes_total = 0
  bytes_by_extension = {}

  for file in files:
    ext = file.suffix.lower()

    if not ext or ext not in FILE_EXTENSIONS:
      logger.debug(f'Discarding extension {ext}')
      continue

    bytes_by_extension.setdefault(ext, 0)

    bytes_in_file = file.stat().st_size
    bytes_total = bytes_total + bytes_in_file
    bytes_by_extension[ext] = bytes_by_extension[ext] + bytes_in_file

  return (bytes_total, bytes_by_extension)


# def select_files(path_to_repo, exclusion_rules = None):
#   """Returns a list of all files that pass the following exclusion rules:
#     1. Exclude if found in .gitignore file
#     2. Exclude dir paths matching known vendors, bundlers, package managers, etc.
#     3. Exclude files matching known vendors, config, metadata, libraries, etc.
#     4. Exclude files with non-programming extensions and binary formats.
#   """

#   # Exclude files from .gitignore if found
#   ignorefiles = use_ignorefile(path_to_repo)

#   # Exclude dirs from known vendors, bundlers, package managers, etc.
  
#   result = []

#   for current_dir, dirnames, filenames in os.walk(path_to_repo):

#     dirnames[:] = [d for d in dirnames if d not in ignorefiles]

#     filtered_files = [f for f in filenames if f not in ignorefiles]

#     result.extend([Path.joinpath(Path(current_dir), Path(f)) for f in filtered_files])

#   return result


# def is_git_repository(dir_path):
#   """Determines whether the provided directory is being tracked by git"""
#   return '.git' in [x.name for x in Path.iterdir(dir_path)]


# def use_ignorefile(path_to_repo):
#   """Checks for the presence of a .gitignore file in the specified directory
#   and returns it as a list with every entry."""

#   # always ignore .git directory
#   result = ['.git']

#   gitignore_file = Path.joinpath(path_to_repo, '.gitignore')

#   if not Path.exists(gitignore_file):
#     return result

#   with open(gitignore_file) as file:
#     result.extend([line.rstrip('/\n') for line in file.readlines() if line != '\n'])
  
#   return result
  

# def branch_exist(path_to_repo, branch_name):
#   """Checks if branch_name exists in the specified git repository"""

#   try:
#     res = subprocess.run(['git', 'branch', '--list', branch_name], capture_output=True, cwd=path_to_repo)
#     return res.stdout
#   except Exception as err:
#     logger.error(err)
#     sys.exit(err.args[0])


# def start_logger(verbosity):
#   """Starts a new logger instance and configures it based on the verbosity argument"""
  
#   stdout_handler = logging.StreamHandler()
#   if verbosity == 1:
#     logger.setLevel(logging.INFO)
#   elif verbosity > 1:
#     logger.setLevel(logging.DEBUG)

#   # Define formatter for the handler
#   fmt = '%(asctime)s [ %(levelname)s ] %(message)s'

#   stdout_handler.setFormatter(CustomFormatter(fmt))
#   logger.addHandler(stdout_handler)


# def print_arguments(args):
#   """Prints the arguments used to run the script."""
  
#   logger.debug(f'Running with arguments: {args}')
#   logger.info(f'Searching repository at location: {args.git_path.resolve()} ({args.branch})')


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