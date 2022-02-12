#!/usr/bin/env python3

from pathlib import Path
from logger.logger import Logger
import subprocess
import sys

# from languages.languages import Language

class Repository:

  def __init__(self, git_path, branch):
    self.logger = Logger.create_logger(__name__)
    self.use_top_level_git_dir(git_path.resolve(), branch = branch)

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


  def use_top_level_git_dir(self, git_path, branch = None):
    """Verifies and changes directories to the root of the git repo"""

    # TODO: Allow to specify branch

    try:  
      res = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        cwd=git_path
      )
      
      root_dir, branch, _ = res.stdout.decode('UTF-8').split('\n')

      if root_dir == '':
        self.logger.warning(f'No git repository found in "{git_path}"')
        sys.exit(1)

      self.entrypoint = root_dir
      self.branch = branch

    except Exception as err:
      self.logger.error(err)
      sys.exit(err.args[0])

  
  def select_files(self, exclude_files = []):
    """Returns a list of all files that pass the following exclusion rules:
      1. Exclude if found in .gitignore file
      2. Exclude dir paths matching known vendors, bundlers, package managers, etc.
      3. Exclude files matching known vendors, config, metadata, libraries, etc.
      4. Exclude files with non-programming extensions and binary formats.
    """

    # TODO: Combine .gitignore and other files from provided list
    ignorefiles = self.gitignore_list()

    result = []

    for current_dir, dirnames, filenames in os.walk(self.entrypoint):

      dirnames[:] = [d for d in dirnames if d not in ignorefiles]

      filtered_files = [f for f in filenames if f not in ignorefiles]

      result.extend([Path.joinpath(Path(current_dir), Path(f)) for f in filtered_files])

    return result

  
  def gitignore_list(self):
    """Checks for the presence of a .gitignore file and returns it as a list"""

    # TODO: use proper git built-in commands to extract info from commits

    # always ignore .git directory
    result = ['.git']

    gitignore_file = Path.joinpath(self.entrypoint, '.gitignore')

    if not Path.exists(gitignore_file):
      return result

    with open(gitignore_file) as file:
      result.extend([line.rstrip('/\n') for line in file.readlines() if line != '\n'])
    
    return result

  # def branch_exist(self) -> bool:
    #   """Checks if branch_name exists in the specified git repository"""

    #   try:
    #     res = subprocess.run(
    #       ['git', 'branch', '--list', self.branch],
    #       capture_output=True,
    #       cwd=self.entrypoint
    #     )
    #     return res.stdout
    #   except Exception as err:
    #     self.logger.error(err)
    #     sys.exit(err.args[0])