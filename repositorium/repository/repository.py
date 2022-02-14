#!/usr/bin/env python3

from pathlib import Path
from itertools import chain
from os import walk
import subprocess
import sys

from logger.logger import Logger
from file.file import FileBlob

class Repository:

  def __init__(self, git_path, branch):
    self._entrypoint = None
    self._branch = None
    self._gitignore = None
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


  def gather_facts(self, vendor_list = None, language_list = None):
    """Gathers facts about the repository such as number of files, size in Kb,
    percentage usage of programming language and markup files, etc"""
    
    # Exclude files that:
    # 1. Are found in repository's .gitignore file
    # 2. Are known locations used by 3rd pty tools, libraries, package managers
    candidate_files = self.select_files(vendor_list, self.gitignore)

    # Valid files are:
    # 1. Programming languages
    # 2. ?
    # 3. ?

    # TODO: fix iterable issue wit hlanguage list which is a dictionary
    valid_files = map(FileBlob, candidate_files, language_list)

    for f in list(valid_files):
      if f.is_valid:
        print(f._path)
      


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
  
  
  def select_files(self, *ignore_list):
    """Returns a list of files not included in the ignore_list provided."""
    
    for current_dir, dirnames, filenames in walk(self.entrypoint):

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
