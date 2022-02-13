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
from logger.logger import Logger

CURRENT_VERSION = '0.0.1'

PROJECT_DIR = Path(__file__).resolve().parent
VENDOR_LIST = Path.joinpath(PROJECT_DIR, 'data', 'vendors.yml')
LANGUAGE_LIST = Path.joinpath(PROJECT_DIR, 'data', 'languages.yml')

def main():
  args = parse_arguments()
  Logger.verbosity = args.verbose
  
  repository = Repository(args.git_path, args.branch)
  # TODO: FIX RECURSION!
  repository.get_facts(VENDOR_LIST, LANGUAGE_LIST)


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