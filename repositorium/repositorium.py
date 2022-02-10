#!/usr/bin/env python3

'''
repositorium.py - Analyze your git reposistory and print statistics such as
primary languages used, number of files, lines of code, etc.

CREDIT: 
https://gist.github.com/ppisarczyk/43962d06686722d26d176fad46879d41
https://github.com/github/linguist/blob/master/lib/linguist/vendor.yml
https://github.com/douban/linguist
'''

from pathlib import Path
import subprocess
import argparse
import logging
import json
import sys
import re
import os

import vendor_code

CURRENT_VERSION = 'v0.0.1'

FILE_EXTENSIONS = json.loads('file_extensions.json')

def main():
  args = parse_arguments()
  start_logger(args.verbose)
  print_arguments(args)

  if args.git_path:
    get_local_repository(args.git_path, args.branch)
  # elif args.git_url:
  #   fetch_remote_repository(args.git_url, args.branch)
  # elif args.username:
  #   fetch_user_data(
  #     args.username,
  #     from_provider=args.provider,
  #     omit_repos=args.omit_repos,
  #     use_repos=args.use_repos
  #   )


def get_local_repository(path_to_repo, branch):
  """Searches for and uses a repository in the local machine to run stats for."""

  entrypoint = entrypoint = Path(path_to_repo).resolve()

  if not is_git_repository(entrypoint):
    logger.warning(f'No git repository found in "{entrypoint}"')
    sys.exit(1)

  if not branch_exist(entrypoint, branch):
    logger.warning(f'No git branch "{branch}" found in "{entrypoint}". Exiting...')
    sys.exit(1)

  repo_files = select_files(entrypoint)
  
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


def select_files(path_to_repo, exclusion_rules = None):
  """Returns a list of all files that pass the following exclusion rules:
    1. Exclude if found in .gitignore file
    2. Exclude dir paths matching known vendors, bundlers, package managers, etc.
    3. Exclude files matching known vendors, config, metadata, libraries, etc.
    4. Exclude files with non-programming extensions and binary formats.
  """

  ignorefiles = use_ignorefile(path_to_repo)
  
  if ignorefiles:
    logger.debug(f'.gitignore file found ({len(ignorefiles)} lines).')
  
  result = []

  for current_dir, dirnames, filenames in os.walk(path_to_repo):

    # TODO: Apply additional filtering rules for both files and dirs, such as:
    # common vendor names, bundled code, known external dependencies, etc.

    # Prune directories and files listed under ignorefiles
    dirnames[:] = [d for d in dirnames if d not in ignorefiles]

    # Exclude files listed under ignorefiles
    filtered_files = [f for f in filenames if f not in ignorefiles]

    result.extend([Path.joinpath(Path(current_dir), Path(f)) for f in filtered_files])
  
  return result





def is_git_repository(dir_path):
  """Determines whether the provided directory is being tracked by git"""
  return '.git' in [x.name for x in Path.iterdir(dir_path)]


def use_ignorefile(path_to_repo):
  """Checks for the presence of a .gitignore file in the specified directory
  and returns it as a list with every entry."""

  gitignore_file = Path.joinpath(path_to_repo, '.gitignore')

  # always ignore .git directory
  result = ['.git']

  if not Path.exists(gitignore_file):
    return result

  with open(gitignore_file) as file:
    result.extend([line.rstrip('/\n') for line in file.readlines() if line != '\n'])
  
  return result
  

def branch_exist(path_to_repo, branch_name):
  """Checks if branch_name exists in the specified git repository"""

  try:
    res = subprocess.run(['git', 'branch', '--list', branch_name], capture_output=True, cwd=path_to_repo)
    return res.stdout
  except Exception as err:
    logger.error(err)
    sys.exit(err.args[0])


def start_logger(verbosity):
  """Starts a new logger instance and configures it based on the verbosity argument"""
  
  stdout_handler = logging.StreamHandler()
  if verbosity == 1:
    logger.setLevel(logging.INFO)
  elif verbosity > 1:
    logger.setLevel(logging.DEBUG)

  # Define formatter for the handler
  fmt = '%(asctime)s [ %(levelname)s ] %(message)s'

  stdout_handler.setFormatter(CustomFormatter(fmt))
  logger.addHandler(stdout_handler)


def print_arguments(args):
  """Prints the arguments used to run the script."""
  
  logger.debug(f'Running with arguments: {args}')

  if args.git_path:
    logger.info(f'Searching repository at location: {args.git_path.resolve()} ({args.branch})')
  
  if args.git_url:
    logger.info(f'Fetching repository url: {args.git_path} ({args.branch})')

  if args.username:
    logger.info(f'Searching for username {args.username} on {args.provider}')

    if args.omit_repos:
      logger.info(f'Ignoring repositories from search: {"".join(args.omit_repos)}')

    if args.use_repos:
      logger.info(f'Searching for reposi repositories from search: {"".join(args.omit_repos)}')
  

def parse_arguments():
  """Parses command line arguments passed to run the script"""

  parser = argparse.ArgumentParser()
  
  source_options = parser.add_mutually_exclusive_group(required=True)
  source_options.add_argument('-d', '--directory',
    help='the git repository path to the source code in the local machine.',
    type=Path,
    dest='git_path',
  )
  source_options.add_argument('-r', '--repo-url',
    help='the git repository url to the source code.',
    dest='git_url',
  )
  source_options.add_argument('-u', '--username',
    help='the username to check all repositores for.',
    metavar='git_username'
  )
  
  lookup_options = parser.add_mutually_exclusive_group()
  lookup_options.add_argument('--omit-repos',
    help='list of git repository names to ignore. Works with username option.',
    nargs='+'
  )
  lookup_options.add_argument('--use-repos',
    help='list of git repositories names to use, ignoring the rest. Works with username option.',
    nargs='+'
  )
  
  parser.add_argument('-b', '--branch',
    help='the git branch to run this script against inside a repository',
    default='main'
  )
  parser.add_argument('-p', '--provider',
    help='specifies the provider to query. Works alongside username option.',
    nargs='+',
    choices=['GitHub', 'GitLab', 'Codeberg'],
    default=['GitHub']
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


# INITIALIZE LOGGER INSTANCE AND CUSTOM FORMATTER
# Custom format class to print using colors. Credit:
# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/

logger = logging.getLogger(__name__)

class CustomFormatter(logging.Formatter):
  """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

  gray = '\x1b[38;5;240m'
  blue = '\x1b[38;5;39m'
  yellow = '\x1b[38;5;220m'
  orange = '\x1b[38;5;202m'
  red = '\x1b[38;5;160m'
  reset = '\x1b[0m'

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