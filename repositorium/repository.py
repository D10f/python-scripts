#!/usr/bin/env python3

from pathlib import Path
from itertools import chain
from re import compile
import mimetypes
import os
import subprocess
import sys

from logger import Logger
from file import File

class Repository:

  def __init__(self, git_path, branch, *exclude_lists):
    self._entrypoint = None
    self._branch = None
    self._gitignore = None
    self._exclude_lists = exclude_lists
    self.logger = Logger.create_logger(__name__)
    self.git_root_dir(git_path.resolve(), branch = branch)


  @property
  def entrypoint(self):
    return self._entrypoint
  

  @entrypoint.setter
  def entrypoint(self, new_path):
    self.logger.info(f'Git entrypoint: {new_path}')
    self._entrypoint = new_path


  @property
  def branch(self):
    return self._branch
  

  @branch.setter
  def branch(self, new_branch):
    self.logger.info(f'Checked-out branch: {new_branch}')
    self._branch = new_branch


  @property
  def gitignore(self):
    if self._gitignore is None:
      self.gitignore_list()
    return self._gitignore


  @gitignore.setter
  def gitignore(self, new_list):
    self.logger.debug(f'Using .gitignore file with {len(new_list)} entries')
    self._gitignore = new_list


  # @property
  # def size(self):
  #   return self._size

  
  # @size.setter
  # def size(self, new_size):
  #   self._size = new_size


  def git_root_dir(self, git_path, branch = None):
    """Verifies and changes directories to the root of the git repo"""

    # TODO: Allow to specify branch

    res = subprocess.run(
      ['git', 'rev-parse', '--show-toplevel', '--abbrev-ref', 'HEAD'],
      capture_output=True,
      cwd=git_path
    )

    if res.returncode == 128:
      self.logger.warning(f'Not a git repository (or any of the parent directories): {git_path}')
      sys.exit(res.returncode)

    # Other errors like not having git installed
    if res.returncode > 0:
      self.logger.error(res.stderr.decode('UTF-8'))
      sys.exit(res.returncode)

    root_dir, branch = res.stdout.decode('UTF-8').strip().split('\n')

    self._entrypoint = Path(root_dir)
    self._branch = branch


  def gather_facts(self):
    """Gathers facts about the repository such as number of files, size in Kb,
    percentage usage of programming language and markup files, etc"""
    
    candidate_files = (File(f) for f in self.select_files(self._exclude_lists, self.gitignore))
    # valid_files = (f for f in candidate_files if f.type in ['programming', 'data'])
    
    for f in candidate_files:
      if f.type in ['programming', 'data']:
        print(f'Name: {f.name}')
        print(f'Size: {f.size}')
        print(f'Language: {f.language}')
        print(f'Extension: {f.extension}')
        print(f'Type: {f.type}')
        print(f'Extension: {f.color}')
        print('---------')


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
  
  
  def select_files(self, *ignore_list):
    """Returns a list of files not included in the ignore_list provided."""

    for current_dir, dirnames, filenames in os.walk(self.entrypoint):

      dirnames[:] = [d for d in dirnames if d not in chain.from_iterable(ignore_list)]

      for f in filenames:
        if f in chain.from_iterable(ignore_list):
          continue
        yield Path.joinpath(Path(current_dir), f)

  
  def gitignore_list(self):
    """Checks for the presence of a .gitignore file and returns it as a list"""

    # TODO: use proper git built-in commands to extract info from commits

    # always ignore .git directory
    result = ['.git']

    gitignore_file = Path.joinpath(self.entrypoint, '.gitignore')

    if not Path.exists(gitignore_file):
      self._gitignore = result
    else:
      with open(gitignore_file) as file:
        result.extend([line.rstrip('/\n') for line in file.readlines() if line != '\n'])
        self._gitignore = result
