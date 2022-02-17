#!/usr/bin/env python3

from pathlib import Path
from itertools import chain
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
    self._lang_size = {}
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


  @property
  def size(self):
    return sum(self.language_sizes.values())
  
  
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
    valid_files = (f for f in candidate_files if (f.type is not None and f.extension != '.json'))
    # valid_files = []

    # for f in candidate_files:
      # print(f.name, f.extension, f.size)
      # valid_files.append(f)

    
    return self.get_language_usage(valid_files)
    

  def get_language_usage(self, files):
    """Returns a list of tuples sorted by the highest language used baesd on
    byte size"""

    self.language_sizes = self.calculate_language_sizes(files)
    total_size = self.size

    for key, value in self.language_sizes.items():
      percentage = round(value * 100 / total_size, 2)
      yield (key, percentage)
    
  
  def calculate_language_sizes(self, files):
    """Increases repository's byte counter by file.size"""
    results = {}
    for f in files:
      results.setdefault(f.language, 0)
      results[f.language] += f.size
    return results


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
