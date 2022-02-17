#!/usr/bin/env python3

'''
repositorium.py - Analyze your git reposistory and print statistics such as
primary languages used, total commits, number of files, etc.

REFERENCES: 
https://gist.github.com/ppisarczyk/43962d06686722d26d176fad46879d41
https://github.com/github/linguist
https://github.com/douban/linguist
'''

from pathlib import Path
from argparse import ArgumentParser
from itertools import chain
import re

from readers import YAMLReaderStrategy, FileReader
from repository import Repository
from logger import Logger
import constants

def main():
  args = parse_arguments()
  Logger.verbosity = args.verbose

  vendor_list = FileReader.read(constants.VENDOR_LIST, YAMLReaderStrategy)
  docs_list = FileReader.read(constants.DOCS_LIST, YAMLReaderStrategy)
  exclude_list = [re.compile(f) for f in chain(vendor_list, docs_list)]

  repository = Repository(args.git_path, args.branch, exclude_list)
  language_usage = repository.gather_facts()
  
  for res in language_usage:
    lang, perc = res
    print(lang, perc)


def parse_arguments():
  """Parses command line arguments passed to run the script"""

  parser = ArgumentParser()
  
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
    version=f'Repositorium.py v{constants.CURRENT_VERSION}'
  )

  return parser.parse_args()


if __name__ == '__main__':
  main()