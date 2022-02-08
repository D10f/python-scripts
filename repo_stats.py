#!/usr/bin/env python3

'''
repo_stats.py - Get statistics about your your project such as lines  of code,
number of files, total size, most common programming language used, etc.
'''

from pathlib import Path
import subprocess
import argparse
import logging
import sys
import os

CURRENT_VERSION = 'v0.0.1'

def main():
  args = parse_arguments()
  start_logger(args.verbose)
  print_arguments(args)

  if args.git_path:
    get_local_repository(args.git_path, args.branch)
  elif args.git_url:
    fetch_remote_repository(args.git_url, args.branch)
  elif args.username:
    fetch_user_data(
      args.username,
      from_provider=args.provider,
      omit_repos=args.omit_repos,
      use_repos=args.use_repos
    )


def get_local_repository(path_to_repo, branch):
  """Searches for and uses a repository in the local machine to run stats for."""

  entrypoint = Path(path_to_repo).resolve()
  is_git_repository = '.git' in [x.name for x in Path.iterdir(entrypoint)]

  if not is_git_repository:
    logger.warning(f'No git repository found in "{entrypoint}"')
    sys.exit(1)

  if not branch_exist(branch, path_to_repo):
    logger.warning(f'No git branch "{branch}" found in "{entrypoint}". Exiting...')
    sys.exit(1)

  ignorefiles = use_ignorefile(path_to_repo)
  
  if ignorefiles:
    logger.debug(f'.gitignore file found ({len(ignorefiles)} lines).')
  
  repo_files = select_files(path_to_repo, ignorefiles)

  # count lines of code per extension (js, ts, css, etc)
  # calculate top used languages in %

# def fetch_remote_repository(url, branch):
#   pass
# def fetch_user_data(username, from_provider = None, omit_repos = None, use_repos = None):
#   pass


def select_files(path_to_repo, ignorefiles):
  """Selects all the files in the given path, recursively."""
  
  result = []

  for current_dir, dirnames, filenames in os.walk(path_to_repo):

    # Prune directories and files listed under ignorefiles
    dirnames[:] = [d for d in dirnames if d not in ignorefiles]

    # Exclude files listed under ignorefiles (converting to path-like)
    result.extend([Path.joinpath(Path(current_dir), Path(f)) for f in filenames])
  
  return result


def use_ignorefile(path_to_repo):
  """Checks for the presence of a .gitignore file in the specified directory"""

  gitignore_file = Path.joinpath(path_to_repo, '.gitignore')

  if not Path.exists(gitignore_file):
    return []

  with open(gitignore_file) as file:
    return [line.rstrip('/\n') for line in file.readlines() if line != '\n']


def branch_exist(branch_name, path_to_repo):
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
  elif verbosity == 2:
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